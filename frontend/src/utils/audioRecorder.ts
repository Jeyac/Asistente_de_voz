/**
 * Graba audio del micrófono y exporta WAV 16 kHz mono (compatible con la API).
 */

const TARGET_SAMPLE_RATE = 16_000;

function encodeWav(samples: Float32Array, sampleRate: number): Blob {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  const writeString = (offset: number, value: string) => {
    for (let i = 0; i < value.length; i += 1) {
      view.setUint8(offset + i, value.charCodeAt(i));
    }
  };

  writeString(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(36, "data");
  view.setUint32(40, samples.length * 2, true);

  let offset = 44;
  for (let i = 0; i < samples.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, sample < 0 ? sample * 0x80_00 : sample * 0x7f_ff, true);
    offset += 2;
  }

  return new Blob([buffer], { type: "audio/wav" });
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

export class AudioRecorder {
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private processor: ScriptProcessorNode | null = null;
  private chunks: Float32Array[] = [];

  async start(): Promise<void> {
    this.mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        channelCount: 1,
      },
    });

    this.audioContext = new AudioContext();
    if (this.audioContext.state === "suspended") {
      await this.audioContext.resume();
    }
    const source = this.audioContext.createMediaStreamSource(this.mediaStream);
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
    this.chunks = [];

    this.processor.onaudioprocess = (event) => {
      const input = event.inputBuffer.getChannelData(0);
      this.chunks.push(new Float32Array(input));
    };

    source.connect(this.processor);
    this.processor.connect(this.audioContext.destination);
  }

  async stop(): Promise<Blob> {
    const sampleRate = this.audioContext?.sampleRate ?? TARGET_SAMPLE_RATE;

    this.processor?.disconnect();
    this.mediaStream?.getTracks().forEach((track) => track.stop());
    await this.audioContext?.close();

    const length = this.chunks.reduce((acc, chunk) => acc + chunk.length, 0);
    const merged = new Float32Array(length);
    let offset = 0;
    for (const chunk of this.chunks) {
      merged.set(chunk, offset);
      offset += chunk.length;
    }

    const resampled = downsample(merged, sampleRate, TARGET_SAMPLE_RATE);
    this.cleanup();
    return encodeWav(resampled, TARGET_SAMPLE_RATE);
  }

  private cleanup(): void {
    this.audioContext = null;
    this.mediaStream = null;
    this.processor = null;
    this.chunks = [];
  }
}
