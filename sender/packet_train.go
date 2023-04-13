package sender

import (
	"fmt"
	"net"
	"strconv"
	"strings"
	"sync"
	"time"
)

type PacketTrainSender struct {
	sender       *UDPSender
	cli          *net.TCPConn // used for communication
	sendSpeed    int
	sendDuration time.Duration
	packetSize   int
}
type PacketTrainSenderOption struct {
	PacketSize int
}

func NewPacketTrainSender(conn *net.TCPConn, option ...PacketTrainSenderOption) *PacketTrainSender {
	sender := &PacketTrainSender{
		sender:       nil,
		cli:          conn,
		sendSpeed:    200,
		sendDuration: time.Millisecond * 100,
		packetSize:   BufferSize,
	}
	if len(option) > 0 {
		sender.packetSize = option[0].PacketSize
	}
	return sender
}

// Connect try to connect to client
func (p *PacketTrainSender) Connect(conn *net.UDPConn, addr *net.UDPAddr) error {
	p.sender = NewUDPSenderWithConn(conn, addr, UDPSenderOption{PacketSize: p.packetSize})
	_, err := p.cli.Write([]byte("ACK"))
	fmt.Println("Connected")
	return err
}

// Serve contains the main logic of packet train
func (p *PacketTrainSender) Serve() {
	defer func() {
		err := p.cli.Close()
		if err != nil {
			fmt.Println(err)
		}
	}()
	for {
		buffer := make([]byte, BufferSize)
		sz, err := p.cli.Read(buffer)
		if err != nil {
			fmt.Println(err)
			return
		}
		messages := string(buffer[:sz])
		messageList := strings.Split(messages, ";")
		for _, message := range messageList {
			if len(message) == 0 {
				continue
			}
			if p.handle(message) {
				return
			}
		}

	}
}

// handle return true if end
func (p *PacketTrainSender) handle(message string) bool {
	fmt.Printf("message: %v\n", message)
	switch message {
	case "END":
		return true
	case "STOP":
		// stop this time
		p.sender.Stop()
	case "USAGE":
		usage := p.sender.ByteCount()
		_, err := p.cli.Write([]byte(fmt.Sprintf("USAGE:%d", usage)))
		if err != nil {
			fmt.Println(err)
		}
	default:
		options := strings.Split(message, ",")
		speed, err := strconv.Atoi(options[0])
		if err != nil {
			fmt.Println(err)
		}
		p.sendSpeed = speed
		duration, err := strconv.Atoi(options[1])
		if err != nil {
			fmt.Println(err)
		}
		p.sendDuration = time.Duration(duration) * time.Millisecond
		go func() {
			p.sender.SendWithSpeedAndTime(p.sendSpeed, p.sendDuration)
			//_, err = p.cli.Write([]byte(strconv.Itoa(byteCount)))
			//if err != nil {
			//	fmt.Println(err)
			//}
		}()
	}
	return false
}

type UDPDispatcher struct {
	activeSenders  map[string]*PacketTrainSender
	pendingSenders map[string]*PacketTrainSender
	activeM        sync.RWMutex
	pendingM       sync.RWMutex
}

func NewUDPDispatcher() *UDPDispatcher {
	return &UDPDispatcher{
		activeSenders:  map[string]*PacketTrainSender{},
		pendingSenders: map[string]*PacketTrainSender{},
	}
}
func (u *UDPDispatcher) Dispatch(udpAddr *net.UDPAddr) {
	listen, err := net.ListenUDP("udp", udpAddr)
	if err != nil {
		panic(err)
	}
	defer listen.Close()
	for {
		buffer := make([]byte, 1024)
		n, addr, err := listen.ReadFromUDP(buffer)
		if err != nil {
			fmt.Println(err)
			continue
		}
		key := string(buffer[:n])
		fmt.Printf("key:%v addr:%v count%v\n", key, addr, n)
		u.pendingM.Lock()
		if sender, ok := u.pendingSenders[key]; ok {
			sender.Connect(listen, addr)
			delete(u.pendingSenders, key)
			u.activeM.Lock()
			u.activeSenders[key] = sender
			u.activeM.Unlock()
			go func() {
				sender.Serve()
				u.activeM.Lock()
				delete(u.activeSenders, key)
				u.activeM.Unlock()
				fmt.Printf("end serving %v\n", key)
			}()
		}
		u.pendingM.Unlock()
	}
}
func (u *UDPDispatcher) AddSender(key string, conn *net.TCPConn, option ...PacketTrainSenderOption) {
	u.pendingM.Lock()
	u.pendingSenders[key] = NewPacketTrainSender(conn, option...)
	u.pendingM.Unlock()
}

type PacketTrainServer struct {
	tcpAddr      *net.TCPAddr
	udpAddr      *net.UDPAddr
	dispatcher   *UDPDispatcher
	senderOption []PacketTrainSenderOption
}

func NewPacketTrainServer(option ...PacketTrainSenderOption) *PacketTrainServer {
	return &PacketTrainServer{senderOption: option}
}
func (p *PacketTrainServer) Listen(tcpAddr *net.TCPAddr, udpAddr *net.UDPAddr) {
	p.tcpAddr = tcpAddr
	p.udpAddr = udpAddr
	p.dispatcher = NewUDPDispatcher()
}

func (p *PacketTrainServer) Run() {
	listen, err := net.ListenTCP("tcp", p.tcpAddr)
	if err != nil {
		panic(err)
	}
	go p.dispatcher.Dispatch(p.udpAddr)
	for {
		conn, err := listen.Accept()
		if err != nil {
			fmt.Println(err)
		}
		tcpConn := conn.(*net.TCPConn)
		buffer := make([]byte, 1024)
		// 先获取客户端指定的key
		sz, err := tcpConn.Read(buffer)
		if err != nil {
			fmt.Println(err)
			continue
		}
		key := string(buffer[:sz])
		p.dispatcher.AddSender(key, tcpConn, p.senderOption...)
	}
}
