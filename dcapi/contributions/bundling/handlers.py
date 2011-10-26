from dcapi.common.handlers import FilterHandler
from dcapi.common.schema import FulltextField
from dcapi.schema import Schema
from dcdata.contribution.models import LobbyistBundlingDenormalized


BUNDLING_SCHEMA = Schema(
    FulltextField('recipient_name', ['committee_name', 'recipient_name']),
    FulltextField('lobbyist_name', ['lobbyist_name', 'firm_name']),
)

def filter_bundling(request):
    return BUNDLING_SCHEMA.build_filter(LobbyistBundlingDenormalized.objects, request)


class BundlingFilterHandler(FilterHandler):
    #fields = CONTRIBUTION_FIELDS
    model = LobbyistBundlingDenormalized
    ordering = ['-amount']
    filename = 'lobbyist_bundled_contributions'

    def queryset(self, params):
        return filter_bundling(self._unquote(params))


