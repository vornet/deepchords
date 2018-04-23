import mido

mid =  mido.MidiFile('little_more_time.mid')

for i, track in enumerate(mid.tracks):
    print('Track {}: {}'.format(i, track.name))
    total_time = 0
    for msg in track:

        if msg.type == 'set_tempo':
            tempo = msg.tempo
        elif msg.type == 'time_signature':
            pass
        else:
            total_time += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
            print(total_time)


    print('done')
    print(mid.length)