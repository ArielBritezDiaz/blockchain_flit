//Flitcoin ICO

// SPDX-License-Identifier: MIT
//Version compiler
pragma solidity ^0.8.0;

contract Flitcoin_ICO {
    //Número máximo de Flitcoins a la venta
    uint public max_flitcoins = 1000000;
    
    //Tasa de conversión de FLT a USD
    uint public usd_to_flitcoins = 1000;

    //Número total de FLT comprados por los inversionistas
    uint public total_flitcoins_bought = 0;

    //Mapeo de dirección de inversionista a activos en Flitcoins y USD
    mapping(address => uint) equity_flitcoins; //la dirección del inversionista va a ser mapeada como un entero
    mapping(address => uint) equity_usd;

    //chequeando si el inversionista puede comprar tokens
    modifier can_buy_flitcoins(uint usd_invested) { //antes de confirmar la compra de flitcoins por la cantidad de dólares que ingresa, con esto chequeamos primeramente que pueda hacerlo
        require(usd_invested * usd_to_flitcoins + total_flitcoins_bought <= max_flitcoins);
        _; //esto significa que las funciones solo serán aplicadas si la condición es verdadera, si puede comprar
    }

    //obteniendo capital invertido en tokens
    function equity_in_flitcoins(address investor) external view returns(uint) { //'external constant' lo ponemos porque no es particular de nuestro smart contract, viene de una fuerza externa
        return equity_flitcoins[investor];
    }

    //obteniendo el capital invertido en dólares(USD)
    function equity_in_usd(address investor) external view returns(uint) {
        return equity_usd[investor];
    }

    //comprando tokens
    function buy_flitcoins(address investor, uint usd_invested) external can_buy_flitcoins(usd_invested) { //antes de entrar a la función usamos el modificador para verificar si el accionista puede comprar flitcoins tomando como parámetro el usd_invested
        //actualizamos el capital en tokens flt del inversionista
        uint flitcoins_bought = usd_invested * usd_to_flitcoins; //los flt comprados es = a la cantidad de usd invertidos * la cantidad de flt que se pueden comprar
        equity_flitcoins[investor] += flitcoins_bought;

        //actualizamos el capital en equity usd
        equity_usd[investor] = equity_flitcoins[investor] / 1000; //queremos saber cuanto tiene el inversionista en dólares

        //actualizamos el total de tokens comprados por el inversionista
        total_flitcoins_bought += flitcoins_bought;
    }

    //vendiendo tokens
    function sell_flitcoins(address investor, uint flitcoins_sold) external {
        //restamos la cantidad de flt vendidos por el inversionista de su cuenta
        equity_flitcoins[investor] -= flitcoins_sold;

        //actualizamos el capital en equity usd
        equity_usd[investor] = equity_flitcoins[investor] / 1000; //queremos saber cuanto tiene el inversionista en dólares

        //actualizamos el total de tokens vendidos por el inversionista
        total_flitcoins_bought -= flitcoins_sold;
    }

}