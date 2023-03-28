#!/bin/bash
echo "export USER_ID=$(id -u)" >> ~/.bashrc
echo "export GROUP_ID=$(id -g)" >> ~/.bashrc
source ~/.bashrc
