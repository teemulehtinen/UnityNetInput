using UnityEngine;

using System;
using System.Collections.Concurrent;
using System.Threading;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Globalization;

public class PositionListener : MonoBehaviour
{
    // Set in GameObect
    public int udpListenerPort;
    public Vector3 origin;
    public Vector3 widthEdge;
    public Vector3 lengthEdge;

    Rigidbody body;
    ConcurrentQueue<Vector2> positionsReceived;
    Thread listener;

    void Start()
    {
        body = GetComponent<Rigidbody>();
        positionsReceived = new ConcurrentQueue<Vector2>();
        listener = new Thread(new ThreadStart(ListenerLoop));
        listener.Start();
    }

    private void ListenerLoop()
    {
        Debug.Log("Receiving positions at port " + udpListenerPort);
        UdpClient client = new UdpClient(udpListenerPort);
        while (true)
        {
            try
            {
                IPEndPoint remote = new IPEndPoint(IPAddress.Any, 0);
                positionsReceived.Enqueue(DecodePosition(client.Receive(ref remote)));
            }
            catch (ThreadAbortException)
            {
                // Ignore end of program.
            }
            catch (Exception e)
            {
                Debug.Log("Error while receiving positions: " + e.ToString());
            }
        }
    }

    private Vector2 DecodePosition(byte[] message)
    {
        string[] xy = Encoding.UTF8.GetString(message).Split(',');
        if (xy.Length != 2)
        {
            throw new FormatException("Not a two part comma separated UTF8 string.");
        }
        return new Vector2(float.Parse(xy[0], CultureInfo.InvariantCulture), float.Parse(xy[1], CultureInfo.InvariantCulture));
    }

    void FixedUpdate()
    {
        while (positionsReceived.TryDequeue(out Vector2 p))
        {
            body.MovePosition(origin + p.x * widthEdge + p.y * lengthEdge);
        }
    }
}
