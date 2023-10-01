# No Imports Allowed!
#6.009 lab 0
# Tharindu Withanage
# collaborators: none

def backwards(sound):
    """
    Parameters
    ----------
    sound : dict with key:value pairs 'rate':int, 'left':list, 'right':list

    Returns
    -------
    dict with left and right lists reversed

    """
    if not sound: # check if dictionary is empty
        return {}
    L = sound['left'][:] # get a copy of the left sound samples
    L.reverse() # reverse the list
    R = sound['right'][:] # get a copy of the right sound samples
    R.reverse() # reverse the list
    return {'rate': sound['rate'], 'left': L, 'right': R} # return a dictionary with the sound samples reversed

def mix(sound1, sound2, p):
    """
    Parameters
    ----------
    sound1 : dict with key:value pairs 'rate':int, 'left':list, 'right':list
    sound2 : dict with key:value pairs 'rate':int, 'left':list, 'right':list
    p : float, 0 <= p <= 1

    Returns
    -------
    a dict with list samples = list elements of sound1 * p + list elements of sound2 * (1-p)

    """
    if sound1['rate'] != sound2['rate']: # check if sampling rate is the same
        return None # return None if different
    k = min(len(sound1['left']), len(sound2['left'])) # get the minimum length of the two sounds
    res = {'rate': sound1['rate']} # initialize a dictionary to store new samples with same sampling rate
    L = [] # initialize list to store left samples
    R = [] # initialize list to store right samples
    for i in range(k): # for each sample
        L.append(sound1['left'][i] * p + sound2['left'][i] * (1 - p)) # modify samples and add to left list
        R.append(sound1['right'][i] * p + sound2['right'][i] * (1 - p)) # modify samples and add to right list
    res['left'] = L # add left samples to dict
    res['right'] = R # add right samples to dict
    return res # return dict with new samples


def echo(sound, num_echos, delay, scale):
    """
    

    Parameters
    ----------
    sound : a dict, representing original sound
    num_echos : int, the number of additional copies of the sound to add
    delay : float, the amount (in seconds) by which each "echo" should be delayed
    scale : float, the amount by which each echo's samples should be scaled

    Returns
    -------
    a dict, with the scaled number of echos specified in the sample

    """
    sample_delay = round(delay * sound['rate']) # get number of samples each copy should be delayed by
    L = sound['left'][:] # create copy of left list
    R = sound['right'][:] # create copy of right list
    # extend lists to incorporate echos
    L += [0] * sample_delay * num_echos
    R += [0] * sample_delay * num_echos
    for i in range(1, num_echos + 1): # go through loop for each echo
        # create lists of scaled values for echo to add to sample
        temp_left = [k * scale ** i for k in sound['left']]
        temp_right = [k * scale ** i for k in sound['right']]
        # go through sample list and add echo samples
        for j in range(len(temp_left)):
            L[j + sample_delay * i] += temp_left[j]
            R[j + sample_delay * i] += temp_right[j]
    
    return {'rate': sound['rate'], 'left': L, 'right': R} # return dictionary with echo samples added
    

def pan(sound):
    """
    Parameters
    ----------
    sound : dict containing original sound samples

    Returns
    -------
    a dict, with right list scaled by increasing coefficients and right list scaled
    with decreasing coefficients

    """
    # get copies of left and right lists
    L = sound['left'][:]
    R = sound['right'][:]
    for k in range(len(L)): # iterate through left and right samples
        R[k] *= k / (len(L) - 1) # scale right samples with increasing scale factors
        L[k] *= 1 - k / (len(L) - 1) # scale left samples with decreasing scale factors
    return {'rate': sound['rate'], 'left': L, 'right': R} # return dict with scaled samples

def remove_vocals(sound):
    """
    Parameters
    ----------
    sound : dict containing original sound samples

    Returns
    -------
    a dict, with vocals removed from samples

    """

    L = sound['left'][:]
    R = sound['right'][:]
    diff = [x - y for x, y in zip(L, R)]
    return {'rate': sound['rate'], 'left': diff, 'right': diff}


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    # 5.1 
    # mystery = load_wav('sounds/mystery.wav')
    # write_wav(backwards(mystery), 'mystery_reversed.wav')
    # # 5.2
    # synth = load_wav('sounds/synth.wav')
    # water = load_wav('sounds/water.wav')
    # write_wav(mix(synth, water, 0.2), 'synth_water.wav')
    # # 5.3
    # chord = load_wav('sounds/chord.wav')
    # write_wav(echo(chord, 5, 0.3, 0.6), 'chord_echo.wav')
    # # 5.4
    # car = load_wav('sounds/car.wav')
    # write_wav(pan(car), 'car_pan.wav')
    # #5.5
    # coffee = load_wav('sounds/coffee.wav')
    # write_wav(remove_vocals(coffee), 'coffee_vocals_removed.wav')
    pass