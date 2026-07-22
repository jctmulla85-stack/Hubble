from governance.logger import get_master_logger
logger = get_master_logger()

class GovernanceAgent:
    def __init__(self, template):
        self.template = template

    def check_status(self, metrics):
        if metrics['drawdown'] > self.template['max_drawdown']:
            logger.critical(f"CRITICAL_DRAWDOWN: {metrics['drawdown']}")
            return "RED", "CRITICAL_DRAWDOWN"
        if metrics['trade_count_hourly'] > self.template['max_trades_per_hour']:
            logger.warning("LOGIC_DRIFT_THROTTLING")
            return "AMBER", "LOGIC_DRIFT_THROTTLING"
        return "GREEN", "OPERATIONAL"
