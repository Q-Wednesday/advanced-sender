package sender

import (
	"fmt"
	"net"
	"strconv"
	"time"
)

type PacketTrainServer struct {
	sender       *UDPSender
	cli          *net.TCPConn // used for communication
	sendSpeed    int
	sendDuration time.Duration
}

func NewPacketTrainServer(conn *net.TCPConn) *PacketTrainServer {
	return &PacketTrainServer{
		sender:       nil,
		cli:          conn,
		sendSpeed:    200,
		sendDuration: time.Millisecond * 100,
	}
}

// Connect try to connect to client
func (p *PacketTrainServer) Connect(addr *net.UDPAddr) {
	p.sender = NewUDPSender(addr)
}

// Serve contains the main logic of packet train
func (p *PacketTrainServer) Serve() {
	defer func() {
		err := p.cli.Close()
		if err != nil {
			fmt.Println(err)
		}
	}()
	for {
		_, err := p.cli.Write([]byte("START"))
		if err != nil {
			fmt.Println(err)
			return
		}
		p.sender.SendWithSpeedAndTime(p.sendSpeed, p.sendDuration)
		buffer := make([]byte, BufferSize)
		sz, err := p.cli.Read(buffer)
		if err != nil {
			fmt.Println(err)
			return
		}
		message := string(buffer[:sz])
		fmt.Printf("message: %v\n", message)
		switch message {
		case "END":
			return
		default:
			speed, err := strconv.Atoi(message)
			if err != nil {
				fmt.Println(err)
				return
			}
			p.sendSpeed = speed

		}
	}
}
