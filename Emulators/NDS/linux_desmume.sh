#!/bin/bash

if ! command -v "$1" &> /dev/null; then
        sudo apt install desmume -y 
    fi

desmume $1