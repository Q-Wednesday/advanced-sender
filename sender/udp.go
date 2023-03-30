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
	rawData   []byte
}

type UDPSenderOption struct {
	PacketSize int
}

func NewUDPSenderWithConn(conn *net.UDPConn, addr *net.UDPAddr, option ...UDPSenderOption) *UDPSender {
	sender := &UDPSender{
		UDPConn:   *conn,
		addr:      addr,
		byteCount: 0,
		stopped:   false,
		speed:     100,
		stopSem:   make(chan struct{}),
		rawData:   rawData,
	}
	if len(option) > 0 {
		sender.rawData = make([]byte, option[0].PacketSize)
		for i := 0; i < len(sender.rawData); i++ {
			sender.rawData[i] = 'A'
		}
	}
	return sender

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
		speed:     100,
		stopSem:   make(chan struct{}),
	}
}

func (s *UDPSender) ByteCount() int {
	return s.byteCount
}

// SendWithSpeed send UDP in a constant speed
func (s *UDPSender) SendWithSpeed(speed int) int {
	startTime := time.Now().UnixMilli()
	byteCount := 0
	var duration int64
	// output in the end
	defer func() {
		s.byteCount += byteCount
		durationMinutes := float64(duration) / 1000
		fmt.Printf("byte count:%v, duration:%v s\n", byteCount, durationMinutes)
		fmt.Printf("average speed: %v MB/s\n", float64(byteCount)/1024/1024/durationMinutes)
	}()

	for {
		select {
		case <-s.stopSem:
			return byteCount
		default:
			duration = time.Now().UnixMilli() - startTime
			if int(duration)*speed*1024*1024/8/1000 > byteCount {
				sz, err := s.WriteToUDP(s.rawData, s.addr)
				if err != nil {
					fmt.Println(err)
					return byteCount
				}
				byteCount += sz
			}
		}
	}
}

func (s *UDPSender) SendWithSpeedAndTime(speed int, t time.Duration) int {
	startTime := time.Now().UnixMilli()
	byteCount := 0
	var duration int64
	// output in the end
	defer func() {
		s.byteCount += byteCount
		durationMinutes := float64(duration) / 1000
		fmt.Printf("byte count:%v, duration:%v s\n", byteCount, durationMinutes)
		fmt.Printf("average speed: %v MB/s\n", float64(byteCount)/1024/1024/durationMinutes)
	}()

	for {
		select {
		case <-s.stopSem:
			return byteCount
		default:
			duration = time.Now().UnixMilli() - startTime
			if int(duration)*speed*1024*1024/8/1000 > byteCount {
				sz, err := s.WriteToUDP(s.rawData, s.addr)
				if err != nil {
					fmt.Println(err)
					return byteCount
				}
				byteCount += sz
			}
			if duration > t.Milliseconds() {
				return byteCount
			}
		}
	}
}

// Send use the default speed to send
func (s *UDPSender) Send() {
	s.SendWithSpeed(s.speed)
}

// Stop the sender
func (s *UDPSender) Stop() {
	s.stopSem <- struct{}{}
}
