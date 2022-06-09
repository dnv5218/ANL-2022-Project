import logging
from operator import index
from pandas import array
from random import randint, random
from sklearn.linear_model import LinearRegression
import traceback
from typing import cast, Dict, List, Set, Collection

from geniusweb.actions.Accept import Accept
from geniusweb.actions.Action import Action
from geniusweb.actions.LearningDone import LearningDone
from geniusweb.actions.Offer import Offer
from geniusweb.actions.PartyId import PartyId
from geniusweb.bidspace.AllBidsList import AllBidsList
from geniusweb.inform.ActionDone import ActionDone
from geniusweb.inform.Finished import Finished
from geniusweb.inform.Inform import Inform
from geniusweb.inform.OptIn import OptIn
from geniusweb.inform.Settings import Settings
from geniusweb.inform.YourTurn import YourTurn
from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.Domain import Domain
from geniusweb.issuevalue.Value import Value
from geniusweb.issuevalue.ValueSet import ValueSet
from geniusweb.party.Capabilities import Capabilities
from geniusweb.party.DefaultParty import DefaultParty
from geniusweb.profile.utilityspace.UtilitySpace import UtilitySpace
from geniusweb.profileconnection.ProfileConnectionFactory import (
    ProfileConnectionFactory,
)
from geniusweb.progress.ProgressRounds import ProgressRounds
from geniusweb.utils import val
from geniusweb.profileconnection.ProfileInterface import ProfileInterface
from geniusweb.profile.utilityspace.LinearAdditive import LinearAdditive
from geniusweb.progress.Progress import Progress
from tudelft.utilities.immutablelist.ImmutableList import ImmutableList
from time import sleep, time as clock
from decimal import Decimal
import sys
from agents.time_dependent_agent.extended_util_space import ExtendedUtilSpace
from tudelft_utilities_logging.Reporter import Reporter


class ExperimentAgent2(DefaultParty):
    def __init__(self, reporter: Reporter = None):
        super().__init__(reporter)
        self._profileint: ProfileInterface = None
        self._utilspace: LinearAdditive = None
        self._me: PartyId = None
        self._progress: Progress = None
        self._receivedBids: list = []
        self._receivedUtils: list = []
        self._lastReceivedBid: Bid = None
        self._lastReceivedUtil: Decimal = None
        self._bestReceivedBid: Bid = None
        self._bestReceivedUtil: Decimal = Decimal(0)
        self._proposalTime: float = None
        self._opponentBidTimes: list = []
        self._extendedspace: ExtendedUtilSpace = None
        self._e: float = 0.1
        self._settings: Settings = None
        self.getReporter().log(logging.INFO, "party is initialized")

    def getCapabilities(self) -> Capabilities:
        return Capabilities(
            set(["SAOP", "Learn", "MOPAC"]),
            set(["geniusweb.profile.utilityspace.LinearAdditive"]),
        )

    def notifyChange(self, info: Inform):
        try:
            if isinstance(info, Settings):
                self._settings = info
                self._me = self._settings.getID()
                self._progress = self._settings.getProgress()
                newe = self._settings.getParameters().get("e")
                if newe != None:
                    if isinstance(newe, float):
                        self._e = newe
                    else:
                        self.getReporter().log(
                            logging.WARNING,
                            "parameter e should be Double but found " + str(newe),
                        )
                protocol: str = str(self._settings.getProtocol().getURI())
                if "Learn" == protocol:
                    val(self.getConnection()).send(LearningDone(self._me))
                else:
                    self._profileint = ProfileConnectionFactory.create(
                        self._settings.getProfile().getURI(), self.getReporter()
                    )
            elif isinstance(info, ActionDone):
                otheract: Action = info.getAction()
                if isinstance(otheract, Offer):
                    self._updateUtilSpace()
                    self._lastReceivedBid = otheract.getBid()
                    self._lastReceivedUtil = self._utilspace.getUtility(self._lastReceivedBid)
            elif isinstance(info, YourTurn):
                if self._proposalTime is not None:
                    time = self._progress.get(clock() * 1000)
                    self._opponentBidTimes.append(time - self._proposalTime)
                self._myTurn()
                self._proposalTime = self._progress.get(clock() * 1000)
            elif isinstance(info, Finished):
                self.getReporter().log(logging.INFO, "Final outcome:" + str(info))
                self.terminate()
                # stop this party and free resources.
        except Exception as ex:
            self.getReporter().log(logging.CRITICAL, "Failed to handle info", ex)
        self._updateRound(info)

    def getE(self) -> float:
        return self._e

    def getDescription(self) -> str:
        return (
            "Time-dependent conceder. Aims at utility u(t) = scale * t^(1/e) "
            + "where t is the time (0=start, 1=end), e is the concession speed parameter (default 1.1), and scale such that u(0)=minimum and "
            + "u(1) = maximum possible utility."
        )

    def terminate(self):
        # self.saveData()
        self.getReporter().log(logging.INFO, "party is terminating:")
        super().terminate()
        if self._profileint != None:
            self._profileint.close()
            self._profileint = None

    def saveData(self):
        data = "Data for learning (see README.md) " + self.other
        with open(f"{self.storage_dir}/{self.other}.md", "w") as f:
            f.write(data)

    ##################### private support funcs #########################

    def _updateRound(self, info: Inform):
        if self._settings == None:
            return
        protocol: str = str(self._settings.getProtocol().getURI())

        if "SAOP" == protocol or "SHAOP" == protocol:
            if not isinstance(info, YourTurn):
                return
        elif "MOPAC" == protocol:
            if not isinstance(info, OptIn):
                return
        else:
            return
        # if we get here, round must be increased.
        if isinstance(self._progress, ProgressRounds):
            self._progress = self._progress.advance()

    def _myTurn(self):
        self._updateUtilSpace()
        # Keep history of received bids and best alternative
        if self._lastReceivedBid is not None:
            self._receivedBids.append(self._lastReceivedBid)
            self._receivedUtils.append(self._lastReceivedUtil)
            if self._lastReceivedUtil > self._bestReceivedUtil:
                self._bestReceivedBid = self._lastReceivedBid
                self._bestReceivedUtil = self._lastReceivedUtil
        # Delay decision if we have to
        # self._delayResponse()
        # Create new bid
        bid = self._makeBid()
        # Check if we've previously gotten a better bid already
        if self._bestReceivedUtil >= self._utilspace.getUtility(bid):
            i = self._receivedUtils.index(self._bestReceivedUtil)
            bid = self._receivedBids.pop(i)
            self._receivedUtils.pop(i)
            # Find next bests
            self._bestReceivedUtil = max(self._receivedUtils)
            i = self._receivedUtils.index(self._bestReceivedUtil)
            self._bestReceivedBid = self._receivedBids[i]
        # Take action
        myAction: Action
        if bid == None or (
            self._lastReceivedBid != None
            and self._utilspace.getUtility(self._lastReceivedBid)
            >= self._utilspace.getUtility(bid)
        ):
            # if bid==null we failed to suggest next bid.
            myAction = Accept(self._me, self._lastReceivedBid)
        else:
            myAction = Offer(self._me, bid)
        self.getConnection().send(myAction)

    def _updateUtilSpace(self) -> LinearAdditive:
        newutilspace = self._profileint.getProfile()
        if not newutilspace == self._utilspace:
            self._utilspace = cast(LinearAdditive, newutilspace)
            self._extendedspace = ExtendedUtilSpace(self._utilspace)
        return self._utilspace

    def _makeBid(self) -> Bid:
        time = self._progress.get(clock() * 1000)

        utilityGoal = self._getUtilityGoal(
            time,
            self.getE(),
            Decimal(0.5),
            self._extendedspace.getMax(),
        )
        options: ImmutableList[Bid] = self._extendedspace.getBids(utilityGoal)
        if options.size() == 0:
            # if we can't find good bid, get max util bid....
            options = self._extendedspace.getBids(self._extendedspace.getMax())
        # pick a random one.
        return options.get(randint(0, options.size() - 1))

    def _getUtilityGoal(
        self, t: float, e: float, minUtil: Decimal, maxUtil: Decimal
    ) -> Decimal:
        ft1 = Decimal(1)
        if e != 0:
            ft1 = round(Decimal(1 - pow(t, 1 / e)), 6)  # defaults ROUND_HALF_UP
        return max(min((minUtil + (maxUtil - minUtil) * ft1), maxUtil), minUtil)

    def _isGood(self, bid: Bid) -> bool:
        if bid == None or self._profileint == None:
            return False
        profile = cast(LinearAdditive, self._profileint.getProfile())
        # the profile MUST contain UtilitySpace
        time = self._progress.get(clock() * 1000)
        return profile.getUtility(bid) >= self._getUtilityGoal(
            time,
            self.getE(),
            Decimal(0.5),
            self._extendedspace.getMax(),
        )

    def _delayResponse(self):
        t = self._progress.get(clock() * 1000)
        if t > 0.95 or self._isGood(self._bestReceivedBid):
            bidTimes = self._opponentBidTimes[-min(len(self._opponentBidTimes), 30):]
            t_o = self._predictBidTime(bidTimes)
            while t < 1 - 5*t_o:
                t = self._progress.get(clock() * 1000)

    def _predictBidTime(self, bidTimes):
        regr = LinearRegression()
        regr.fit(array(range(len(bidTimes))).reshape(-1, 1), array(bidTimes).reshape(-1, 1))
        return regr.predict(array([len(bidTimes)]).reshape(1, 1))
