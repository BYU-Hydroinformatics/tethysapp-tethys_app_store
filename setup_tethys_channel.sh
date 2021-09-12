#!/bin/bash

tethys settings --set CHANNEL_LAYERS.default.BACKEND channels.layers.InMemoryChannelLayer
echo "Websocket Channel configured for Tethys App Store"