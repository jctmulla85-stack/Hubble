from circuit_breaker import GovernanceAgent
from metrics_monitor import get_live_metrics
from governance.logger import get_master_logger

logger = get_master_logger()
SAFETY = {"max_drawdown": 0.05, "max_trades_per_hour": 50}

def audit_live_performance():
    metrics = get_live_metrics() # Reads from your live trading_audit.log
    status, reason = GovernanceAgent(SAFETY).check_status(metrics)

    if status == "RED":
        # AUDIT ALERT: The bot is currently in a state that violates your safety rules
        logger.critical(f"AUDIT ALERT: Live bot currently in violation: {reason}")
    else:
        logger.info("AUDIT: Live bot operating within safety parameters.")

if __name__ == "__main__":
    audit_live_performance()
