#!/bin/bash

list_file=$(./vpn_utils.py init)

if (( 0 != $? ));
then
    exit 1
fi

chosen_vpn=$(percol $list_file)
ovpn_files_dir=$(./vpn_utils.py choose "$chosen_vpn" $list_file)
vpn_file=$(cd $ovpn_files_dir && ls *.ovpn | percol)
sudo openvpn $ovpn_files_dir/$vpn_file
./vpn_utils.py clean $list_file
