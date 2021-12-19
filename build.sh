#!/bin/sh

pyinstaller main.spec --noconfirm && dist/main/main
