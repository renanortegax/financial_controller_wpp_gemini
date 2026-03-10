import re
from datetime import datetime, timedelta
from app.config import log_config

logger = log_config('app.utils.model_manager')


class ModelManager:
    def __init__(self, models: list = None):
        """
        models: lista com os modelos em ordem de preferencia
        """
        if not hasattr(self, 'models'):  # só seta se ainda não existir
            self.models = models or []
        if not hasattr(self, 'blocked_until'):
            self.blocked_until = {}

    def _is_blocked(self, model) -> bool:
        blocked = self.blocked_until.get(model.model_name)
        if blocked and datetime.now() < blocked:
            logger.warning("Modelo %s bloqueado até %s", model.model_name, blocked.strftime("%Y-%m-%dT%H:%M:%S"))
            return True
        
        return False
    
    def _block_model(self, model, error_str: str):
        if "free_tier_requests" in error_str or "per_day" in error_str.lower():
            seconds = 60*60*24
            logger.warning("Modelo %s atingiu limite DIÁRIO (RPD) — bloqueado por 24h", model.model_name)
        else:
            seconds = self._extract_retry_delay_error(error_str) or 60
            logger.warning("Modelo %s atingiu limite por MINUTO (RPM) — bloqueado por %ds", model.model_name, seconds)

        unblock_at = datetime.now() + timedelta(seconds=seconds)
        self.blocked_until[model.model_name] = unblock_at
        logger.warning("Modelo %s será liberado em %s", model.model_name, unblock_at.strftime('%Y-%m-%d %H:%M:%S'))

    def _extract_retry_delay_error(self, error_str: str) -> int | None:
        match = re.search(r'seconds:\s*(\d+)', error_str)
        return int(match.group(1)) if match else None
    
    def generate_content(self, prompt, **kwargs):
        logger.debug("Modelos no self do ModelManager: %s", [model.model_name for model in self.models])
        for model in self.models:
            if self._is_blocked(model):
                continue
            try:
                logger.info("Usando modelo: %s", model.model_name)
                return model.generate_content(prompt, **kwargs)

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "ResourceExhausted" in error_str:
                    self._block_model(model, error_str)
                else:
                    logger.error("Erro inesperado no modelo %s: %s", model.model_name, e)
                    raise

        raise Exception("Todos os modelos estão indisponíveis no momento.")