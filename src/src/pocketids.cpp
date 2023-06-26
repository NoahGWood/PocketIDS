#include <set>
#include <ctime>
#include <pcap.h>
#include <fstream>
#include <iostream>
#include <sstream>
#include <cstring>
#include <algorithm>
#include <arpa/inet.h>
#include <net/ethernet.h>
#include <netinet/ether.h>
#include <libnotify/notify.h>

using namespace std;

static uid_t euid, ruid;

string dangerousIPFile;
set<std::string> dangerousIP;
set<std::string> foundIP;

NotifyNotification *NOTIF;
pcap_t *DESCR;

void get_root(void)
{
    int status;
#ifdef _POSIX_SAVED_IDS
    status = seteuid(euid);
#else
    status = setreuid(ruid, euid);
#endif
    if (status < 0)
    {
        cerr << "Couldn't set uid" << endl;
        exit(status);
    }
}

void get_normal(void)
{
    int status;
#ifdef _POSIX_SAVED_IDS
    status = seteuid(ruid);
#else
    status = setreuid(euid, euid);
#endif
    if (status < 0)
    {
        cerr << "Couldn't set uid" << endl;
        exit(status);
    }
}

/*
 * Structure of an internet header, naked of options.
 *
 * Stolen from tcpdump source (thanks tcpdump people)
 *  - and then stolen again from Stanford :P (thanks stanford)
 *
 * We declare ip_len and ip_off to be short, rather than u_short
 * pragmatically since otherwise unsigned comparisons can result
 * against negative integers quite easily, and fail in subtle ways.
 */
struct my_ip
{
    u_int8_t ip_vhl; /* header length, version */
#define IP_V(ip) (((ip)->ip_vhl & 0xf0) >> 4)
#define IP_HL(ip) ((ip)->ip_vhl & 0x0f)
    u_int8_t ip_tos;               /* type of service */
    u_int16_t ip_len;              /* total length */
    u_int16_t ip_id;               /* identification */
    u_int16_t ip_off;              /* fragment offset field */
#define IP_DF 0x4000               /* dont fragment flag */
#define IP_MF 0x2000               /* more fragments flag */
#define IP_OFFMASK 0x1fff          /* mask for fragmenting bits */
    u_int8_t ip_ttl;               /* time to live */
    u_int8_t ip_p;                 /* protocol */
    u_int16_t ip_sum;              /* checksum */
    struct in_addr ip_src, ip_dst; /* source and dest address */
};

string getTime()
{
    time_t now = time(nullptr);
    string nowstring = ctime(&now);
    if (!nowstring.empty() && nowstring[nowstring.length() - 1] == '\n')
    {
        nowstring.erase(nowstring.length() - 1);
    }
    return nowstring;
}

void loadFile()
{
    ifstream f;
    string line;
    f.open(dangerousIPFile);
    if (f.is_open())
    {
        while (getline(f, line))
        {
            if (line.find("#") == string::npos)
            { // Don't add commented lines
                stringstream ss(line);
                string _ip;
                getline(ss, _ip, '\t');
                dangerousIP.insert(_ip);
            }
        }
    }
}

void makeNotification(string ip)
{
    get_normal();
    string message = "Dangerous IP address found at: ";
    message += ip;
    NOTIF = notify_notification_new("PocketIDS",
                                    message.c_str(),
                                    "distributor-logo");
    notify_notification_set_timeout(NOTIF, 10000); // 10 seconds
    if (!notify_notification_show(NOTIF, 0))
    {
        cerr << "Notification failed to show: "
             << message << endl;
    }
    get_root();
}

void packetHandler(u_char *userData, const struct pcap_pkthdr *pkthdr, const u_char *packet)
{
    const struct ether_header *eptr;
    const struct my_ip *ip;
    uint length = pkthdr->len;
    uint off;
    int i, len;

    // Load the header from the packet
    eptr = (struct ether_header *)packet;

    // Jump pass the ethernet header
    ip = (struct my_ip *)(packet + sizeof(struct ether_header));
    length -= sizeof(struct ether_header);

    /* check to see we have a packet of valid length */
    if (length < sizeof(struct my_ip))
    {
        printf("truncated ip %d", length);
    }
    len = ntohs(ip->ip_len);

    /* Check to see if we have the first fragment */
    off = ntohs(ip->ip_off);
    if ((off & 0x1fff) == 0) /* aka no 1's in first 13 bits */
    {
        bool badFound = false;
        if (dangerousIP.find((string)inet_ntoa(ip->ip_src)) != dangerousIP.end() && foundIP.find((string)inet_ntoa(ip->ip_src)) == foundIP.end())
        {
            badFound = true;
            foundIP.insert((string)inet_ntoa(ip->ip_src));
            makeNotification((string)inet_ntoa(ip->ip_src));
        }
        else if (dangerousIP.find((string)inet_ntoa(ip->ip_dst)) != dangerousIP.end())
        {
            if (foundIP.find((string)inet_ntoa(ip->ip_dst)) == foundIP.end())
            {
                badFound = true;
                foundIP.insert((string)inet_ntoa(ip->ip_dst));
                makeNotification((string)inet_ntoa(ip->ip_dst));
            }
        }
        if (badFound)
        {
            cout << getTime() << "-";
            // Output the correct packet type
            switch (ntohs(eptr->ether_type))
            {
            case ETHERTYPE_AARP:
                cout << "(AARP) ";
                break;
            case ETHERTYPE_ARP:
                cout << "(ARP) ";
                break;
            case ETHERTYPE_AT:
                cout << "(AT) ";
                break;
            case ETHERTYPE_IP:
                cout << "(IP) ";
                break;
            case ETHERTYPE_IPV6:
                cout << "(IPV6) ";
                break;
            case ETHERTYPE_IPX:
                cout << "(IPX) ";
                break;
            case ETHERTYPE_LOOPBACK:
                cout << "(LOOP) ";
                break;
            case ETHERTYPE_NTRAILER:
                cout << "(NTRAIL) ";
                break;
            case ETHERTYPE_PUP:
                cout << "(PUP) ";
                break;
            case ETHERTYPE_REVARP:
                cout << "(REVARP) ";
                break;
            case ETHERTYPE_SPRITE:
                cout << "(SPRITE) ";
                break;
            case ETHERTYPE_TRAIL:
                cout << "(TRAIL) ";
                break;
            case ETHERTYPE_VLAN:
                cout << "(VLAN)";
                break;
            case ETHER_TYPE_LEN:
                cout << "(LEN) ";
                break;
            default:
                cout << "(???) ";
                break;
            }
            // Output src/dest IP addresses
            cout << "Dangerous IP Found: ";
            cout << "SRC " << inet_ntoa(ip->ip_src);
            cout << " DST " << inet_ntoa(ip->ip_dst);
            cout << endl;
        }
    }
}

void cleanup()
{
    // Release libnotify resources
    notify_uninit();
    // Release pcap resources
    if (DESCR != nullptr)
    {
        pcap_close(DESCR);
        DESCR = nullptr;
    }
}

int Run()
{
    get_normal();
    // Initialize libnotify
    if (notify_init("PocketIDS") != true)
    {
        cerr << "Failed to initialize libnotify" << endl;
        return 1;
    }

    // Register cleanup function to be called at exit
    if (atexit(cleanup) != 0)
    {
        cerr << "Failed to register exit handler" << endl;
        return 1;
    }
    NOTIF = notify_notification_new("PocketIDS",
                                    "Scan Started",
                                    "security-high-symbolic");
    cout << getTime() << "- PocketIDS: Scan Started..." << endl;
    if (!notify_notification_show(NOTIF, 0))
    {
        cerr << "show has failed" << endl;
        return -1;
    }
    char *dev;
    char errbuf[PCAP_ERRBUF_SIZE];

    // Get IP addresses from file
    loadFile();
    // Get a device to peak into
    get_root();
    dev = pcap_lookupdev(errbuf);
    if (dev == NULL)
    {
        cout << "pcap_lookupdev() failed: " << errbuf << endl;
        return 1;
    }

    DESCR = pcap_open_live(dev, BUFSIZ, 0, -1, errbuf);
    if (DESCR == NULL)
    {
        cout << "pcap_open_live() failed: " << errbuf << endl;
        return 1;
    }
    if (pcap_loop(DESCR, -1, packetHandler, NULL) < 0)
    {
        cout << "pcap_loop() failed: " << pcap_geterr(DESCR);
        return 1;
    }
    cout << "Capture finished" << endl;
    get_normal();
    return 0;
}

int Help() {
    cout << "PocketIDS Usage:\n\tpocketids -h\tDisplays Usage Information\n\tpocketids -i bad_ip_files" << endl;
    exit(0);
}

int main(int argc, char *argv[])
{
    int c;
    ruid = getuid();
    euid = geteuid();
    while ((c = getopt(argc, argv, "hi:")) != -1)
    {
        switch (c)
        {
        case 'h':
            Help();
        case 'i':
            dangerousIPFile = optarg;
            cout << "Input file: " << dangerousIPFile << endl;
            break;
        default:
            Help();
        }
    }
    if(dangerousIPFile.empty()) {
        cout << "Input file required." << endl << endl;
        Help();
    }
    // Now run the program
    c = Run();
    return c;
}