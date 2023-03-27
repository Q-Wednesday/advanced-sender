package sender

import (
	"fmt"
	"net"
	"time"
)

var rawDataA []byte
var rawDataB []byte

const BufferSize = 1024

func init() {
	rawDataA = make([]byte, BufferSize)
	for i := 0; i < len(rawDataA); i++ {
		rawDataA[i] = 'A'
	}
	rawDataB = make([]byte, BufferSize)
	for i := 0; i < len(rawDataB); i++ {
		rawDataB[i] = 'B'
	}
}

type UDPSender struct {
	net.UDPConn
	addr      *net.UDPAddr
	byteCount int
	stopped   bool // may be deprecated
	interval  int  //ms
	startTime int64
	stopSem   chan struct{} // send to this chan to stop sending
}

func NewUDPSenderWithConn(conn *net.UDPConn, addr *net.UDPAddr) *UDPSender {
	return &UDPSender{
		UDPConn:   *conn,
		addr:      addr,
		byteCount: 0,
		stopped:   false,
		interval:  10,
		stopSem:   make(chan struct{}),
	}

}
func NewUDPSender(addr *net.UDPAddr) *UDPSender {
	conn, err := net.ListenUDP("udp", &net.UDPAddr{
		IP:   net.IPv4(0, 0, 0, 0),
		Port: 9877,
	})
	if err != nil {
		panic(err)
	}
	return &UDPSender{
		UDPConn:   *conn,
		addr:      addr,
		byteCount: 0,
		stopped:   false,
		interval:  10,
		stopSem:   make(chan struct{}),
	}
}

func (u *UDPSender) ByteCount() int {
	return u.byteCount
}

// SendWithInterval send a pair of UDP packets
func (s *UDPSender) SendWithInterval(interval int) {
	startTime := time.Now().UnixMilli()
	endTime := time.Now().UnixMilli()
	byteCountA := 0
	byteCountB := 0
	// output in the end
	defer func() {
		fmt.Printf("Startat:%v\n", startTime)
		fmt.Printf("byte count A:%v, byte count B:%v s\n", byteCountA, byteCountB)
		fmt.Printf("invertal: %v ms\n", interval)
		fmt.Printf("Endat:%v\n", endTime)
		fmt.Printf("Duration:%v", endTime - startTime)
	}()

	szA, err := s.WriteToUDP(rawDataA, s.addr)
	if err != nil {
		fmt.Println(err)
		return
	}
	byteCountA = szA

	time.Sleep(time.Duration(interval)*time.Millisecond)

	szB, err := s.WriteToUDP(rawDataB, s.addr)
	if err != nil {
		fmt.Println(err)
		return
	}
	byteCountB = szB

	endTime = time.Now().UnixMilli()

	return

	//for {
	//	select {
	//	case <-s.stopSem:
	//		return
	//	default:
	//		duration = time.Now().UnixMilli() - startTime
	//		if int(duration)*speed*1024*1024/8/1000 > byteCount {
	//			sz, err := s.WriteToUDP(rawDataA, s.addr)
	//			if err != nil {
	//				fmt.Println(err)
	//				return
	//			}
	//			byteCount += sz
	//		}
	//	}
	//}
}

//func (s *UDPSender) SendWithSpeedAndTime(speed int, t time.Duration) {
//	go func() {
//		time.Sleep(t)
//		s.Stop()
//	}()
//	s.SendWithSpeed(speed)
//}

// Send use the default speed to send
//func (s *UDPSender) Send() {
//	s.SendWithSpeed(s.speed)
//}

// Stop the sender
//func (s *UDPSender) Stop() {
//	s.stopSem <- struct{}{}
//}
