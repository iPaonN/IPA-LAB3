#!/usr/bin/env python3

from textfsmlab import connect_device, get_description, autoset_description

def test_R1():
    """Test router 1"""
    conn = connect_device("R1")
    
    autoset_description(conn)
    
    assert get_description(conn, "Gi0/1") == "Connect to PC"
    assert "Connect to" in get_description(conn, "Gi0/2")
    
    conn.disconnect()

def test_R2():
    """Test router 2"""
    conn = connect_device("R2")
    
    autoset_description(conn)
    
    assert get_description(conn, "Gi0/3") == "Connect to WAN"
    assert "Connect to" in get_description(conn, "Gi0/1")
    assert "Connect to" in get_description(conn, "Gi0/2")
    
    conn.disconnect()

def test_S1():
    """Test switch 1"""
    conn = connect_device("S1")
    
    autoset_description(conn)
    
    assert get_description(conn, "Gi0/3") == "Connect to PC"
    assert "Connect to" in get_description(conn, "Gi0/1")
    
    conn.disconnect()

if __name__ == '__main__':
    print("Running tests...")
    
    print("Testing R1...")
    test_R1()
    print("✅ R1 passed")
    
    print("Testing R2...")
    test_R2()
    print("✅ R2 passed")
    
    print("Testing S1...")
    test_S1()
    print("✅ S1 passed")
    
    print("All tests passed!")
