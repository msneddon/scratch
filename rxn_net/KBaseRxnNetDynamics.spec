/*


*/
module KBaseRxnNetDynamics {

  /*
  @id ws KBaseRxnNetDynamics.ReactionNetwork
  */
  typedef string rxn_net_id;


  typedef string species_name;
  typedef string rxn_name;
  
  typedef string sbml_file;
  
  
  typedef string parameter_name;
  typedef string parameter_expression;
  
  
  /*
  @optional description
  */
  typedef structure {
    parameter_name name;
    parameter_expression expression;
    string description;
  } Parameter;
  
  /*
  @optional name description
  */
  typedef structure {
    string name;
    string description;
    list <Parameter> parameters;
  } ParameterSet;
  
  /*
  @
  */
  typedef structure {
    string type;
    string rate_expression;
  } RateLaw;
  
  /*
    @optional name
    @optional stoichiometry
  */
  typedef structure {
    list <species_name> reactants;
    list <species_name> products;
    list <int> stoichiometry;
    RateLaw rate;
    rxn_name name;
  } Reaction;

  /*
  @optional description
  */
  typedef structure {
    species_name name;
    string description;
  } MolecularSpecies;


  /*
  */
  typedef structure {
     string name;
     string description;
     list <MolecularSpecies> species;
     list <Reaction> reactions;
  } ReactionNetwork;
  
  
  typedef structure {
    rxn_net_id rxn_network;
    
  
  } InitialConditions;


  /* Model vs. ModelSet */

  funcdef sbml_to_rxn_network(sbml_file sbml) returns ();
  funcdef create_rxn_network_from_sbml(sbml_file sbml) returns ();
  
  
  
  
  funcdef create_rxn_network(list<ReactionNetwork>) returns ();
  
  funcdef simulate_ode(ParameterSet, InitialConditions, ReactionNetwork) returns ();


};
