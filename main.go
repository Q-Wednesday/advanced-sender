package main

import (
	"github.com/Q-Wednesday/advanced-sender/sender"
	"net"
	"time"
)

func testUDPSender() {
	// send to localhost:9876
	udpSender := sender.NewUDPSender(&net.UDPAddr{IP: net.ParseIP("192.168.1.243"), Port: 9876})
	for i:=0;i<20;i++ {
		udpSender.SendWithInterval(10)
		time.Sleep(1000 * time.Millisecond)
	}
	// stop sender after 6 minutes
	//go func() {
	//	time.Sleep(100 * time.Millisecond)
	//	udpSender.Stop()
	//}()
	//udpSender.Send()

}

func main() {
	//s := &sender.UDPSender{}
	//s.Listen(
	//	&net.UDPAddr{
	//	IP:   net.IPv4(0, 0, 0, 0),
	//	Port: 9877,
	//})
	//s.Run()
	testUDPSender()
}
