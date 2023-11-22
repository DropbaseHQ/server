import unittest.mock

class DropbaseRouterMocker:
    def __init__(self):
        self.patches: list[tuple[str, str, callable]] = []

    def patch(self, sub_router_name: str, method_name: str, *, side_effect: callable):
        self.patches.append((sub_router_name, method_name, side_effect))

    def get_mock_dropbase_router(self, *args, **kwargs):
        mock_router = unittest.mock.MagicMock()
        for sub_router_name, method_name, side_effect in self.patches:
            method = getattr(getattr(mock_router, sub_router_name), method_name)
            method.side_effect = side_effect
        return mock_router
