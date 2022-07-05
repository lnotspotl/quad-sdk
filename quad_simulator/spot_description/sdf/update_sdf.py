#!/usr/bin/env python

import os

def main():
	os.system("gz sdf -p ../urdf/spot.urdf > ./spot.sdf")
	os.system("sed -i -e 's/spot_description//g' ./spot.sdf")

if __name__ == "__main__":
	main()