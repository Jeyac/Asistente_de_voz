/**
 * Captura continua del micrófono para detección de «Hey Jarvis».
 *
 * Emite fragmentos PCM int16 mono a 16 kHz (1280 muestras = 2560 bytes),
 * formato esperado por POST /activation/score-chunk(s).
 */

/** Muestras por fragmento (~80 ms a 16 kHz). */
export const WAKE_CHUNK_SAMPLES = 1280;
const TARGET_SAMPLE_RATE = 16_000;

function floatToInt16(samples: Float32Array): Int16Array {
  const out = new Int16Array(samples.length);
  for (let i = 0; i < samples.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    out[i] = sample < 0 ? sample * 0x80_00 : sample * 0x7f_ff;
  }
  return out;
}

function downsample(buffer: Float32Array, inputRate: number, outputRate: number): Float32Array {
  if (outputRate === inputRate) return buffer;
  const ratio = inputRate / outputRate;
  const newLength = Math.round(buffer.length / ratio);
  const result = new Float32Array(newLength);
  for (let i = 0; i < newLength; i += 1) {
    result[i] = buffer[Math.round(i * ratio)];
  }
  return result;
}

/** Stream de micrófono dedicado al wake word (separado del grabador de comandos). */
export class WakeWordMicStream {
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private processor: ScriptProcessorNode | null = null;
  private pending: number[] = [];

  async start(onChunk: (chunk: Int16Array) => void): Promise<void> {
    this.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        channelCount: 1,
      },
    });

    this.audioContext = new AudioContext({ sampleRate: TARGET_SAMPLE_RATE });
    // En iOS/Safari el contexto arranca suspendido hasta resume() explícito.
    if (this.audioContext.state === "suspended") {
      await this.audioContext.resume();
    }

    const inputRate = this.audioContext.sampleRate;
    const source = this.audioContext.createMediaStreamSource(this.mediaStream);
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
    this.pending = [];

    this.processor.onaudioprocess = (event) => {
      const input = event.inputBuffer.getChannelData(0);
      const resampled = downsample(new Float32Array(input), inputRate, TARGET_SAMPLE_RATE);
      for (let i = 0; i < resampled.length; i += 1) {
        this.pending.push(resampled[i]);
      }
      while (this.pending.length >= WAKE_CHUNK_SAMPLES) {
        const slice = this.pending.splice(0, WAKE_CHUNK_SAMPLES);
        onChunk(floatToInt16(Float32Array.from(slice)));
      }
    };

    // Salida en silencio: el procesador debe estar conectado pero sin reproducir eco.
    const silent = this.audioContext.createGain();
    silent.gain.value = 0;
    source.connect(this.processor);
    this.processor.connect(silent);
    silent.connect(this.audioContext.destination);
  }

  async stop(): Promise<void> {
    this.processor?.disconnect();
    this.mediaStream?.getTracks().forEach((track) => track.stop());
    await this.audioContext?.close();
    this.processor = null;
    this.mediaStream = null;
    this.audioContext = null;
    this.pending = [];
  }
}
