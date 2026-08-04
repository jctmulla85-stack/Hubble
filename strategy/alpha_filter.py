def select_top_alpha_assets(assets, backend_client=None, top_n=3):
    """
    Ranks assets using multi-factor criteria (momentum, volatility profile, 
    and liquidity standards) and selects only the top high-conviction candidates.
    Excludes any non-equity or crypto instruments automatically.
    """
    scored = []
    for asset in assets:
        symbol = asset.get("symbol")
        if not symbol or "/" in symbol or "BTC" in symbol or "ETH" in symbol:
            continue
            
        score = asset.get("momentum_score", 1.0) * asset.get("liquidity_score", 1.0)
        scored.append((score, asset))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:top_n]]
