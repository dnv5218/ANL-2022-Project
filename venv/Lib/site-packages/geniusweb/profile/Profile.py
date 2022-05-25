from abc import ABC
from typing import Optional

from pyson.JsonSubTypes import JsonSubTypes
from pyson.JsonTypeInfo import Id, As
from pyson.JsonTypeInfo import JsonTypeInfo

from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.Domain import Domain


@JsonTypeInfo(use=Id.NAME, include=As.WRAPPER_OBJECT)
@JsonSubTypes(["geniusweb.profile.utilityspace.LinearAdditiveUtilitySpace.LinearAdditiveUtilitySpace"])
class Profile(ABC): 
	'''
	Profile is a very general object describing how much a {@link Bid} is
	preferred. "is preferred" can be worked out in different ways, eg by a
	function "isBetter" that says if bid1 is preferred over bid2, or by assigning
	utility values to each bid that says how much I like that particular bid. All
	profiles should be implemented immutable
	'''

	def getName(self)->str:
		'''
		@return the name of this profile. Must be simple name (a-Z, 0-9)
		'''
		
	def getDomain(self)->Domain :
		'''
		@return the domain in which this profile is defined.
		'''
		
	def getReservationBid(self) -> Optional[Bid] :
		'''
		@return a (hypothetical) bid that is the best alternative to a
		        non-agreement. Only bids that are equal or better should be
		        accepted. If a negotiation does not reach an agreement, the party
		        can get this offer somewhere else. This replaces the older notion
		        of a "reservation value" and is more general. If None, there is
		        no reservation bid and any agreement is better than no agreement.
		        This bid can be partial.
		'''

