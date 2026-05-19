"""TensorFlow + palabras clave del dataset (intenciones nuevas sin reentrenar)."""
from asistente_voz.domain.entities.prediction_result import PredictionResult
from asistente_voz.infrastructure.ml.keyword_intent_matcher import KeywordIntentMatcher
from asistente_voz.infrastructure.ml.tensorflow.inference.predictor import IntentPredictor

class HybridIntentPredictor:
    """Usa el modelo Keras y refuerza con ejemplos del JSON si hace falta."""

    def __init__(self, tensorflow_predictor: IntentPredictor, keyword_matcher: KeywordIntentMatcher, fallback_intent: str) -> None:
        """Inicializa la instancia."""
        self._tf = tensorflow_predictor
        self._keywords = keyword_matcher
        self._fallback_intent = fallback_intent

    def predict(self, text: str) -> PredictionResult:
        """Realiza la predicción."""
        tf_result = self._tf.predict(text)
        keyword_hit = self._keywords.match(text)
        if not keyword_hit:
            return tf_result
        kw_intent, kw_confidence = keyword_hit
        if kw_intent == tf_result.intent and tf_result.above_threshold:
            return tf_result
        use_keyword = not tf_result.above_threshold or tf_result.intent == self._fallback_intent or kw_intent not in tf_result.probabilities or (tf_result.probabilities.get(kw_intent, 0.0) < 0.05)
        if not use_keyword and tf_result.confidence >= 0.9:
            return tf_result
        probabilities = dict(tf_result.probabilities)
        probabilities[kw_intent] = max(kw_confidence, probabilities.get(kw_intent, 0.0))
        return PredictionResult(intent=kw_intent, confidence=kw_confidence, raw_text=tf_result.raw_text, cleaned_text=tf_result.cleaned_text, above_threshold=True, probabilities=probabilities)
