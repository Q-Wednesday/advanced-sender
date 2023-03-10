package main

import (
	"github.com/Q-Wednesday/advancedSender/sender"
	"net"
	"time"
)

func main() {
	// send to localhost:9876
	udpSender := sender.NewUDPSender(&net.UDPAddr{IP: net.ParseIP("127.0.0.1"), Port: 9876})
	udpSender.SendWithSpeedAndTime(100, 100*time.Millisecond)
	// stop sender after 6 minutes
	go func() {
		time.Sleep(100 * time.Millisecond)
		udpSender.Stop()
	}()
	udpSender.Send()

}
