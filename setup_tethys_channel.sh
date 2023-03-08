#!/bin/bash

tethys settings --get | grep -q "'CHANNEL_LAYERS'"
if [ $? == 0 ];
then
    echo "Websocket Channel layer has been already set for the app store"
else
    tethys settings --set CHANNEL_LAYERS.default.BACKEND channels.layers.InMemoryChannelLayer
    echo "Websocket Channel configured for Tethys App Store"
fi
