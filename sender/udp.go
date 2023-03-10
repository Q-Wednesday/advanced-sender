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
	stopped   bool
	speed     int //Mbps
	startTime int64
	stopSem   chan struct{}
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
func (s *UDPSender) Send() {
	s.startTime = time.Now().UnixMilli()
	for {
		select {
		case <-s.stopSem:
			duration := float64(time.Now().UnixMilli()-s.startTime) / 1000
			fmt.Printf("byte count:%v, duration:%v s\n", s.byteCount, duration)
			fmt.Printf("average speed: %v MB/s", float64(s.byteCount)/1024/1024/duration)
			return
		default:
			delta := time.Now().UnixMilli() - s.startTime
			if int(delta)*s.speed*1024*1024/8/1000 > s.byteCount {
				sz, err := s.WriteToUDP(rawData, s.addr)
				if err != nil {
					panic(err)
				}
				s.byteCount += sz
			}
		}
	}
}

func (s *UDPSender) Stop() {
	s.stopSem <- struct{}{}
}
