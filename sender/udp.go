package sender

import (
	"fmt"
	"net"
	"time"
)

var rawData []byte

const BufferSize = 1024

func init() {
	rawData = make([]byte, BufferSize)
	for i := 0; i < len(rawData); i++ {
		rawData[i] = 'A'
	}
}

type UDPSender struct {
	net.UDPConn
	addr      *net.UDPAddr
	byteCount int
	stopped   bool // may be deprecated
	speed     int  //Mbps
	startTime int64
	stopSem   chan struct{} // send to this chan to stop sending
}

func NewUDPSender(addr *net.UDPAddr) *UDPSender {
	conn, err := net.ListenUDP("udp", nil)
	if err != nil {
		panic(err)
	}
	return &UDPSender{
		UDPConn:   *conn,
		addr:      addr,
		byteCount: 0,
		stopped:   false,
		speed:     100,
		stopSem:   make(chan struct{}),
	}
}

// SendWithSpeed send UDP in a constant speed
func (s *UDPSender) SendWithSpeed(speed int) {
	startTime := time.Now().UnixMilli()
	byteCount := 0
	var duration int64
	// output in the end
	defer func() {
		durationMinutes := float64(duration) / 1000
		fmt.Printf("byte count:%v, duration:%v s\n", byteCount, durationMinutes)
		fmt.Printf("average speed: %v MB/s\n", float64(byteCount)/1024/1024/durationMinutes)
	}()

	for {
		select {
		case <-s.stopSem:
			return
		default:
			duration = time.Now().UnixMilli() - startTime
			if int(duration)*speed*1024*1024/8/1000 > byteCount {
				sz, err := s.WriteToUDP(rawData, s.addr)
				if err != nil {
					panic(err)
				}
				byteCount += sz
			}
		}
	}
}

func (s *UDPSender) SendWithSpeedAndTime(speed int, t time.Duration) {
	go func() {
		time.Sleep(t)
		s.Stop()
	}()
	s.SendWithSpeed(speed)
}

// Send use the default speed to send
func (s *UDPSender) Send() {
	s.SendWithSpeed(s.speed)
}

// Stop the sender
func (s *UDPSender) Stop() {
	s.stopSem <- struct{}{}
}
