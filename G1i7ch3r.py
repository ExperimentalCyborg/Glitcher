#! /usr/bin/python3

import os
import sys
import random
import argparse
from PIL import Image

logo = '''   ▄████  ██▓     ██▓▄▄▄█████▓ ▄████▄   ██░ ██ ▓█████  ██▀███  
  ██▒ ▀█▒▓██▒    ▓██▒▓  ██▒ ▓▒▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▓██ ▒ ██▒
 ▒██░▄▄▄░▒██░    ▒██▒▒ ▓██░ ▒░▒▓█    ▄ ▒██▀▀██░▒███   ▓██ ░▄█ ▒
 ░▓█  ██▓▒██░    ░██░░ ▓██▓ ░ ▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒██▀▀█▄  
 ░▒▓███▀▒░██████▒░██░  ▒██▒ ░ ▒ ▓███▀ ░░▓█▒░██▓░▒████▒░██▓ ▒██▒
  ░▒   ▒ ░ ▒░▓  ░░▓    ▒ ░░   ░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ▒▓ ░▒▓░
   ░   ░ ░ ░ ▒  ░ ▒ ░    ░      ░  ▒    ▒ ░▒░ ░ ░ ░  ░  ░▒ ░ ▒░
 ░ ░   ░   ░ ░    ▒ ░  ░      ░         ░  ░░ ░   ░     ░░   ░ 
       ░     ░  ░ ░           ░ ░       ░  ░  ░   ░  ░   ░
        Breaks images in an aesthetically pleasing manner.\n'''


def perr(msg, err):
    """
    Print an error message
    :param msg: Message
    :param err: Exception object
    """
    print('{}: {}: {}'.format(msg, type(err).__name__, err))


def clean_path(path):
    if isinstance(path, str):
        return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
    else:
        return path


def get_settings():
    """
    Parse commandline arguments.
    :return: a dict of settings.
    """

    ap = argparse.ArgumentParser(description='Apply artificial data corruption to images.')
    ap_gen = ap.add_argument_group('General')
    ap_gen.add_argument('--no-logo', action='store_true', help='Clean up your automation log files!')
    ap_gen.add_argument('--out-path', type=str, metavar='path', default=None, help='Where to store the results')
    ap_gen.add_argument('--seed', type=int, metavar='integer', default=None,
                        help='The same seed with the same input generates the same output every time.\n'
                             'The effects will also be identical for multiple images with identical dimensions '
                             'and file types.')
    ap_gen.add_argument('--skip-first', type=int, metavar='percent', default=0, help='Leave the first x%% original.')
    ap_gen.add_argument('--skip-last', type=int, metavar='percent', default=0, help='Leave the last x%% original.')

    ap_eff_togg = ap.add_argument_group('Effect toggles')
    ap_eff_togg.add_argument('--glitch-channels-together', action='store_true', help='Apply the same effect to all channels.')
    ap_eff_togg.add_argument('--no-hard-noise', action='store_true', help='Disable the hard noise effect.')
    ap_eff_togg.add_argument('--no-soft-noise', action='store_true', help='Disable the soft noise effect.')
    ap_eff_togg.add_argument('--no-skip', action='store_true', help='Disable the multiple/shifted image effect.')
    ap_eff_togg.add_argument('--no-none', action='store_true', help='Disable the unmodified image effect.')
    ap_eff_togg.add_argument('--no-max', action='store_true', help='Disable channel whiteout effect.')
    ap_eff_togg.add_argument('--no-min', action='store_true', help='Disable the channel blackout effect.')

    ap_eff_tun = ap.add_argument_group('Effect tuning')
    ap_eff_tun.add_argument('--skip-step-size', type=int, metavar='pixels', default=1, help='step size for skip effect')
    ap_eff_tun.add_argument('--hard-noise-min', type=int, metavar='percent', default=0, help='minimum effect size')
    ap_eff_tun.add_argument('--hard-noise-max', type=int, metavar='percent', default=3, help='maximum effect size')
    ap_eff_tun.add_argument('--soft-noise-min', type=int, metavar='percent', default=0, help='minimum effect size')
    ap_eff_tun.add_argument('--soft-noise-max', type=int, metavar='percent', default=5, help='maximum effect size')
    ap_eff_tun.add_argument('--skip-min', type=int, metavar='percent', default=2, help='minimum effect size')
    ap_eff_tun.add_argument('--skip-max', type=int, metavar='percent', default=8, help='maximum effect size')
    ap_eff_tun.add_argument('--none-min', type=int, metavar='percent', default=2, help='minimum effect size')
    ap_eff_tun.add_argument('--none-max', type=int, metavar='percent', default=30, help='maximum effect size')
    ap_eff_tun.add_argument('--max-min', type=int, metavar='percent', default=0, help='minimum effect size')
    ap_eff_tun.add_argument('--max-max', type=int, metavar='percent', default=1, help='maximum effect size')
    ap_eff_tun.add_argument('--min-min', type=int, metavar='percent', default=0, help='minimum effect size')
    ap_eff_tun.add_argument('--min-max', type=int, metavar='percent', default=3, help='maximum effect size')

    ap.add_argument('files', nargs='+', metavar='img_file_path',
                    help='One or more file(s) to glitch, or one folder only containing images (may be mixed types)')

    args = vars(ap.parse_args())

    # Convert percentages to internally expected floats
    args['skip_first'] /= 100
    args['skip_last'] /= 100
    args['hard_noise_min'] /= 100
    args['hard_noise_max'] /= 100
    args['soft_noise_min'] /= 100
    args['soft_noise_max'] /= 100
    args['skip_min'] /= 100
    args['skip_max'] /= 100 
    args['none_min'] /= 100
    args['none_max'] /= 100 
    args['max_min'] /= 100 
    args['max_max'] /= 100 
    args['min_min'] /= 100 
    args['min_max'] /= 100 

    args['out_path'] = clean_path(args['out_path'])

    return args


def do_glitch(file_path, settings):
    print("Loading image")
    try:
        im = Image.open(file_path)
    except OSError as e:
        perr('Unable to load image', e)
        return

    print('Format: {}'.format(im.format))
    print('Dimensions: {}x{}'.format(*im.size))
    print('Mode: {}'.format(im.mode))
    channel_names = im.getbands()
    print('Channels: {} ({})'.format(len(channel_names), ', '.join(channel_names)))

    if settings['seed'] is None:
        seed = random.randint(100000000, 999999999)
        print('Random seed: {}'.format(seed))
    else:
        seed = settings['seed']

    channels = im.split()
    mode = im.mode
    del im
    new_channels = []
    for i, ch in enumerate(channels):
        print('Glitching channel {}'.format(channel_names[i]))

        if not settings['glitch_channels_together']:
            seed += i
        new_channels.append(glitch_channel(ch, seed, **settings))  # Offset the seed so the channels will be unique

    im_out = Image.merge(mode, new_channels)

    file_path = os.path.basename(file_path)
    outfile = file_path[:file_path.rfind('.')]
    outformat = 'PNG'
    print('Saving image')
    filepath = '{}.glitched.{}'.format(outfile, outformat)
    if settings['out_path'] is not None:
        filepath = os.path.join(settings['out_path'], filepath)
    im_out.save(filepath)


def glitch_channel(channel,
                   custom_seed=0,
                   skip_first=0,
                   skip_last=0,
                   **kwargs):

    random.seed(custom_seed)

    buf = channel.tobytes()
    buflen = len(buf)
    newbuf = bytearray(buflen)
    start_at = round(buflen * skip_first)
    end_at = round(buflen - (buflen * skip_last))

    # Populate the actions based on the settings
    actions = []  # (function, min_size, max_size

    if not kwargs['no_hard_noise']:
        actions.append((glitch_action_noise, kwargs['hard_noise_min'], kwargs['hard_noise_max']))
    if not kwargs['no_soft_noise']:
        actions.append((glitch_action_noise_add, kwargs['soft_noise_min'], kwargs['soft_noise_max']))
    if not kwargs['no_skip']:
        actions.append((glitch_action_skip, kwargs['skip_min'], kwargs['skip_max']))
    if not kwargs['no_none']:
        actions.append((glitch_action_none, kwargs['none_min'], kwargs['none_max']))
    if not kwargs['no_max']:
        actions.append((glitch_action_max, kwargs['max_min'], kwargs['max_max']))
    if not kwargs['no_min']:
        actions.append((glitch_action_min, kwargs['min_min'], kwargs['min_max']))

    # decide a strategy
    strategy = []
    while sum([l for a, l in strategy]) < end_at - start_at:  # while strategies combined do not fill gitchable area
        index = random.randint(0, len(actions)-1)
        action = actions[index][0]
        length = random.randint(round(buflen*actions[index][1]), round(buflen*actions[index][2]))
        strategy.append([action, length])

    for i, c in enumerate(buf[:start_at]):  # copy the untouched parts at the beginning
        newbuf[i] = c

    for i, c in enumerate(buf[end_at:]):  # copy the untouched parts at the end
        newbuf[i+end_at] = c

    origin_offset = 0
    for i in range(start_at, end_at):  # glitch!
        if i + origin_offset >= buflen:
            origin_offset = -i
        elif i + origin_offset < 0:
            origin_offset = buflen - i -1

        origin_offset = strategy[0][0](newbuf, buf, i, origin_offset, **kwargs)

        strategy[0][1] -= 1  # Decrement this strategy's length
        if strategy[0][1] < 1:  # delete it if it's run out, so [0] points to the next one
            del strategy[0]

    del buf
    return Image.frombytes(channel.mode, channel.size, bytes(newbuf))


def glitch_action_none(buf_new, buf_original, index, offset_original, **kwargs):
    buf_new[index] = buf_original[index]
    return offset_original


def glitch_action_skip(buf_new, buf_original, index, offset_original, **kwargs):
    buf_new[index] = buf_original[index+offset_original]
    offset_original += kwargs['skip_step_size']
    return offset_original


def glitch_action_min(buf_new, buf_original, index, offset_original, **kwargs):
    buf_new[index] = 0
    return offset_original


def glitch_action_max(buf_new, buf_original, index, offset_original, **kwargs):
    buf_new[index] = 255
    return offset_original


def glitch_action_noise(buf_new, buf_original, index, offset_original, **kwargs):
    buf_new[index] = random.randrange(0, 256)
    return offset_original


def glitch_action_noise_add(buf_new, buf_original, index, offset_original, **kwargs):
    buf_new[index] = round((buf_original[index+offset_original] + random.randrange(0, 256)) /2)
    return offset_original


if __name__ == '__main__':
    if '--no-logo' not in sys.argv:
        print(logo)

    s = get_settings()

    s['files'] = [clean_path(p) for p in s['files']]  # Clean up the paths
    if len(s['files']) == 1 and os.path.isdir(s['files'][0]):
        s['files'] = [os.path.join(s['files'][0], p)
                      for p in os.listdir(s['files'][0])
                      if os.path.isfile(os.path.join(s['files'][0], p))]

    print()
    for index, f in enumerate(s['files']):
        print('Image {}/{}: {}'.format(index+1, len(s['files']), f))
        do_glitch(f, s)
        print()
