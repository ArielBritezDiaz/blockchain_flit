// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.8.0;

contract NewClient {

    uint128 private incrementValue; //increment for id uint in struct Client
    uint8 private quantityShare; //increment for quantitiyShare for uint8 quantityShares in struct Client
    
    //The users in Flit are Clients
    struct Client {
        uint id;
        address addr;
        string username;
        int balance;
        int availableBalance;
        int fund;
        uint8 quantityShares;
        bool status;
    }

    //Each Client in Flit is recognized with uint
    mapping(uint => Client) private clients;
    mapping(address => uint) private clientsAddress;
    mapping(string => address) private clientsUsername;

    function CreateClient(string calldata _username) public returns(address) {
        require(bytes(_username).length > 0, "The username cannot be empty");
        require(clientsUsername[_username] == address(0), "This user already exists.");

        clients[incrementValue] = Client(incrementValue, msg.sender, _username, 0, 0, 0, quantityShare, true);
        clientsAddress[msg.sender] = incrementValue;
        incrementValue ++;
        return msg.sender;
    }

    //Get info Client of Flit
    function GetClient(string calldata _username) public view returns(uint, address, string memory, uint8, bool) {
        require(bytes(_username).length > 0, "The username cannot be empty");

        for(uint i = 0; i < incrementValue; i++) {
            if(keccak256(abi.encodePacked(clients[i].username)) == keccak256(abi.encodePacked(_username))) {
                return (clients[i].id, clients[i].addr, clients[i].username, clients[i].quantityShares, clients[i].status);
            }
        }
        revert("User not found");
    }

    //Get the wallet of the client
    function GetWalletClient(address _addr) public view returns(string memory, address, int, int, int, uint8, bool) {
        require(clients[clientsAddress[msg.sender]].status, "The account must be activated");

        for(uint i = 0; i < quantityShare; i++) {
            if(keccak256(abi.encodePacked(clients[i].addr)) == keccak256(abi.encodePacked(_addr))) {
                return (clients[i].username, clients[i].addr, clients[i].balance, clients[i].availableBalance, clients[i].fund, clients[i].quantityShares, clients[i].status);
            }
        }
        revert("Wallet not found");
    }

    //Post a new balance to increase
    function IncreaseAvailableBalance() public payable {
        require(clients[clientsAddress[msg.sender]].status, "The account must be activated");
        require(msg.value > 0, "The value to increase balance must be greater than zero");

        clients[clientsAddress[msg.sender]].availableBalance += int(msg.value);
        clients[clientsAddress[msg.sender]].balance += int(msg.value); // Adjust balance calculation
        quantityShare ++;
    }

    function DecreaseAvailableBalance() public payable {
        require(clients[clientsAddress[msg.sender]].status, "The account must be activated");
        require(msg.value > 0, "The value to decrease balance must be greater than zero");

        clients[clientsAddress[msg.sender]].availableBalance -= int(msg.value);
        clients[clientsAddress[msg.sender]].balance -= int(msg.value); // Adjust balance calculation
        quantityShare ++;
    }

    //payment client to client
    function PaymentClient(address _addr) public payable {
        require(clients[clientsAddress[msg.sender]].status, "The account must be activated");
        require(msg.value > 0, "The value to increase balance must be greater than zero");
        require(int(msg.value) <= clients[clientsAddress[msg.sender]].availableBalance, "The value to transfer must be less than or equal to the current balance");

        clients[clientsAddress[msg.sender]].availableBalance -= int(msg.value);
        clients[clientsAddress[_addr]].availableBalance += int(msg.value);
        clients[clientsAddress[msg.sender]].balance -= int(msg.value); // Adjust balance calculation
        quantityShare ++;
    }

    //deposit new found
    function DepositFund() public payable {
        require(clients[clientsAddress[msg.sender]].status, "The account must be activated");
        require(msg.value > 0, "The value to increase balance must be greater than zero");
        require(int(msg.value) <= clients[clientsAddress[msg.sender]].availableBalance, "The value to decrease balance must be less than the current balance");

        clients[clientsAddress[msg.sender]].availableBalance -= int(msg.value);
        clients[clientsAddress[msg.sender]].fund += int(msg.value);
        quantityShare ++;
    }

    //for withdraw the funds
    function ToWithdrawFund() public payable {
        require(clients[clientsAddress[msg.sender]].status, "The account must be activated");
        require(msg.value > 0, "The value to increase balance must be greater than zero");
        require(int(msg.value) <= clients[clientsAddress[msg.sender]].fund, "The value to decrease balance must be less than the current balance");

        clients[clientsAddress[msg.sender]].fund -= int(msg.value);
        clients[clientsAddress[msg.sender]].availableBalance += int(msg.value); // Adjust balance calculation
        quantityShare ++;
    }

    //to deactivate a user
    function InactiveClient() public {
        require(clients[clientsAddress[msg.sender]].status, "The account must be activated");

        clients[clientsAddress[msg.sender]].status = false;
    }

    //to activate a user
    function ReactiveClient() public {
        require(!clients[clientsAddress[msg.sender]].status, "The account is already active");

        clients[clientsAddress[msg.sender]].status = true;
    }
}