def test_session_singleton():
    from investment_portfolio import CachedRateLimitedSession

    session_1 = CachedRateLimitedSession()
    from investment_portfolio import CachedRateLimitedSession

    session_2 = CachedRateLimitedSession()
    assert session_1.core is session_2.core
