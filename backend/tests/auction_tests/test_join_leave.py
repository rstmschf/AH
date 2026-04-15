import pytest
from auctions.models import AuctionParticipant


AUC_URL = "/api/v1/auctions/"
AUC_URL_DETAIL = "/api/v1/auctions/{auction_id}/"


@pytest.mark.django_db
class TestAuctionJoinLeave:
    def _url(self, auction):
        return AUC_URL_DETAIL.format(auction_id=auction.id)

    def test_other_user_can_join_via_link(self, api_client, auction, other_user):
        invite_code = auction.invite_code

        api_client.force_authenticate(other_user)
        response = api_client.post(f"{AUC_URL}join/{invite_code}/")

        assert response.status_code == 200
        assert AuctionParticipant.objects.filter(
            participant=other_user, auction=auction
        ).exists()

    def test_joined_user_gets_visibility(self, api_client, auction, other_user):
        invite_code = auction.invite_code
        api_client.force_authenticate(other_user)
        before_response = api_client.get(self._url(auction))
        assert before_response.status_code == 404

        join_response = api_client.post(f"{AUC_URL}join/{invite_code}/")
        assert join_response.status_code == 200

        after_response = api_client.get(self._url(auction))
        assert after_response.status_code == 200

    def test_left_participant_loses_visibility(self, api_client, auction, participant):
        api_client.force_authenticate(participant)

        before_response = api_client.get(self._url(auction))
        assert before_response.status_code == 200

        leave_response = api_client.post(f"{self._url(auction)}leave/")
        assert leave_response.status_code == 200

        after_response = api_client.get(self._url(auction))
        assert after_response.status_code == 404