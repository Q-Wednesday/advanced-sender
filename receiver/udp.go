package receiver

import (
	"fmt"
	"github.com/Q-Wednesday/advancedSender/sender"
	"net"
)

func Receive() {
	data := make([]byte, sender.BufferSize)
	serverSocket, err := net.ListenUDP("udp", &net.UDPAddr{
		IP:   net.IPv4(0, 0, 0, 0),
		Port: 9876,
	})
	if err != nil {
		panic(err)
	}
	for {
		sz, _, err := serverSocket.ReadFromUDP(data)
		if err != nil {
			panic(err)
		}
		fmt.Println(sz)
		fmt.Println(data)
	}
}
