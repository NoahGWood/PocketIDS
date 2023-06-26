g++ *.cpp -L/usr/lib -lpcap `pkg-config --cflags --libs libnotify` -o PocketIDS
sudo chown root: PocketIDS
sudo chmod a+s PocketIDS
mv PocketIDS ../PocketIDS