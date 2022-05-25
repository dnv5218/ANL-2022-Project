package geniusweb.profile;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonIgnore;

import geniusweb.issuevalue.Bid;
import geniusweb.issuevalue.Domain;

/**
 * Set up such that jackson can look at the getters.
 *
 */
public abstract class DefaultProfile implements Profile {
	private final String name;
	private final Domain domain;
	private final Bid reservationbid;

	/**
	 * 
	 * @param name           the name for the profile
	 * @param domain         the {@link Domain} description
	 * @param reservationbid the reservation {@link Bid}
	 */
	@JsonCreator
	public DefaultProfile(String name, Domain domain, Bid reservationbid) {
		this.name = name;
		this.domain = domain;
		this.reservationbid = reservationbid;
		if (reservationbid != null) {
			String message = domain.isFitting(reservationbid);
			if (message != null)
				throw new IllegalArgumentException(
						"reservationbid is not fitting domain: " + message);
		}

	}

	@Override
	public String getName() {
		return name;
	}

	@Override
	public Domain getDomain() {
		return domain;
	}

	@Override
	public Bid getReservationBid() {
		return reservationbid;
	}

	/**
	 * 
	 * @return string of values contained in here. Useful to make derived
	 *         toString functions
	 */
	@JsonIgnore
	public String getValuesString() {
		return name + "," + domain + "," + reservationbid;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((domain == null) ? 0 : domain.hashCode());
		result = prime * result + ((name == null) ? 0 : name.hashCode());
		result = prime * result
				+ ((reservationbid == null) ? 0 : reservationbid.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		DefaultProfile other = (DefaultProfile) obj;
		if (domain == null) {
			if (other.domain != null)
				return false;
		} else if (!domain.equals(other.domain))
			return false;
		if (name == null) {
			if (other.name != null)
				return false;
		} else if (!name.equals(other.name))
			return false;
		if (reservationbid == null) {
			if (other.reservationbid != null)
				return false;
		} else if (!reservationbid.equals(other.reservationbid))
			return false;
		return true;
	}

}
