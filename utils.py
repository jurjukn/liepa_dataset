import contextlib
import soundfile as sf
import numpy as np
import resampy
import wave

def fix_length(data, size, axis=-1, **kwargs):
    kwargs.setdefault('mode', 'constant')

    n = data.shape[axis]

    if n > size:
        slices = [slice(None)] * data.ndim
        slices[axis] = slice(0, size)
        return data[slices]

    elif n < size:
        lengths = [(0, 0)] * data.ndim
        lengths[axis] = (0, size - n)
        return np.pad(data, lengths, **kwargs)

    return data

def resample_data(y, orig_sr, target_sr, **kwargs):
    if orig_sr == target_sr:
        return y

    ratio = float(target_sr) / orig_sr
    n_samples = int(np.ceil(y.shape[-1] * ratio))

    y_hat = resampy.resample(y, orig_sr, target_sr, filter='kaiser_best', axis=-1)
    y_hat = fix_length(y_hat, n_samples, **kwargs)

    return np.ascontiguousarray(y_hat, dtype=y.dtype)

def resample(path, src_sr, dst_sr):
    y, sr = sf.read(path)
    assert src_sr == sr
    y_r = resample_data(y, src_sr, dst_sr)
    sf.write(path, y_r, dst_sr, subtype='PCM_32')


def wav_duration(path):
    with contextlib.closing(wave.open(path,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return (frames / float(rate)), frames, rate
