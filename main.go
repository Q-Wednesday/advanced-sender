package main

import (
	"fmt"
	"github.com/Q-Wednesday/advancedSender/sender"
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

// TODO server应该要及时清理和释放
var servers map[string]*sender.PacketTrainServer

func dispatchUDP() {
	listen, err := net.ListenUDP("udp", &net.UDPAddr{
		IP:   net.IPv4(0, 0, 0, 0),
		Port: 9876,
	})
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
		if server, ok := servers[key]; ok {
			server.Connect(addr)
			go func() {
				server.Serve()
				delete(servers, key)
				fmt.Printf("end serving %v\n", key)
			}()
		} else {
			fmt.Printf("cannot find key %v\n", key)
		}
	}
}
func main() {
	listen, err := net.Listen("tcp", ":8000")
	if err != nil {
		panic(err)
	}
	servers = make(map[string]*sender.PacketTrainServer)
	go dispatchUDP()
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
		servers[key] = sender.NewPacketTrainServer(tcpConn)
	}
}
