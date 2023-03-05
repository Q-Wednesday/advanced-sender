package main

import (
	"github.com/Q-Wednesday/advancedSender/sender"
	"net"
	"time"
)

func main() {
	// send to localhost:9876
	udpSender := sender.NewUDPSender(&net.UDPAddr{IP: net.ParseIP("127.0.0.1"), Port: 9876})
	// stop sender after 6 minutes
	go func() {
		time.Sleep(5 * time.Second)
		udpSender.Stop()
	}()
	udpSender.Send()

}
