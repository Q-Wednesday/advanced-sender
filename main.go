package main

import (
	"github.com/Q-Wednesday/advanced-sender/sender"
	"net"
	"time"
)

func testUDPSender() {
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

func main() {
	s := &sender.PacketTrainServer{}
	s.Listen(&net.TCPAddr{
		IP:   net.IPv4(0, 0, 0, 0),
		Port: 8000,
	}, &net.UDPAddr{
		IP:   net.IPv4(0, 0, 0, 0),
		Port: 9876,
	})
	s.Run()
}
