const Flitcoin = artifacts.require('Flitcoin_ICO');

module.exports = function (deployer) {
  deployer.deploy(Flitcoin);
};