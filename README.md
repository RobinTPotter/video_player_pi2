# video_player_pi2

moving on from webapps for a bit, started to look at pygame with a view to learning its control system and very basic functions.

seems a quite elegent way of doing graphics development on pi (excluding 3d from what I can see).

this is a video player, partly done that should suit me better than Kodi did, being far too flabby for its own good.

control cycle is very basic, using a variable MODE for mode, from a list of MODES with static values, stolen code from adafruit as noted therein.

config of video is done via the config file which is a json object. specify array of directories to "search" for videos in, also configure the extensions it will view as video files.

ultimately (like video_player_pi before it) this is a front end for omxplayer.

bye then
