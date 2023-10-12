import libsbml
import numpy as np
import matplotlib.pyplot as plt
import tellurium as te
import roadrunner as rr

# Load an SBML file and check for errors
def load_sbml_model(sbml_file_path):
    document = libsbml.readSBMLFromFile(sbml_file_path)

    if document.getNumErrors()>0:
        print("SBML errors: ")
        print(document.getErrorLog().toString())
        return None

    #Get the model from the document
    model = document.getModel()
    if model is None:
        print("No model found in the SBMl file")
        exit()

    return model

#Input the file path to load the SBML file
sbml_file_path = input("Enter the path to your SBML file: ")
model = load_sbml_model(sbml_file_path)


# #Get the list of species from the model
# species_list=[species.getId() for species in model.getListOfSpecies()]

# user inputs a product from the model to be maximized and a kinetic parameter from the model to be varied for said maximization
# product_id = input("Enter the product ID of the product from the model you wish to maximize: ")
# kinetic_parameter_id = input("Enter the ID of the kinetic parameter to be varied for product optimization: ")

# # # user inputs a range over which the kinetic parameter symmetrically varies
# value_range = float(input("Enter the range over which the input kinetic parameter will symmetrically be varied for poduct optimization: "))
# resolution = 100

#Arrays to store parameter values and corresponding product concentrations
# parameter_values = np.linspace(
#     model.getParameter(kinetic_parameter_id).getValue() - value_range/2,
#     model.getParameter(kinetic_parameter_id).getValue() + value_range/2,
#     resolution
# )





def get_rate_law(model):
    rate_law = []
    for reaction in model.getListOfReactions():
        rate_law.append(libsbml.formulaToString(reaction.getKineticLaw().getMath()))
    return rate_law


parameter_ids = []

rate_laws = get_rate_law(model)


for parameters in model.getListOfParameters():
    parameter_ids.append(parameters.getId())

species_initial_concentrations = {}
for species in model.getListOfSpecies():
    species_id = species.getId()
    initial_concentration = species.getInitialConcentration()
    species_initial_concentrations[species_id] = initial_concentration


products_by_reaction = []

for reaction in model.getListOfReactions():
    products_in_reaction = []

    for product in reaction.getListOfProducts():
        species_id = product.getSpecies()
        species = model.getSpecies(species_id)
        if not species.getConstant():
            initial_concentration = species.getInitialConcentration()
            products_in_reaction.append(initial_concentration)

    products_by_reaction.append(products_in_reaction)

non_constant_reaction_products_list = []

for reaction in model.getListOfReactions():
    # Get the non-constant products of the reaction
    non_constant_products = [
        product.getSpecies()
        for product in reaction.getListOfProducts()
        if not model.getSpecies(product.getSpecies()).getConstant()
    ]

    # Add the non-constant products to the list
    non_constant_reaction_products_list.append(non_constant_products)


rate_law_species=[]

for j in range(len(rate_laws)):
# Split the rate law into individual components (species, operators, etc.)
    components = rate_laws[j].split()

    for k in range(len(components)):
        component = components[k]
        if component in species_initial_concentrations:
            rate_law_species.append(component)
        elif component.strip('()') in species_initial_concentrations:
            rate_law_species.append(component.strip('()'))

rate_law_species = list(dict.fromkeys(rate_law_species))

stoichiometries_by_reaction = []

for reaction in model.getListOfReactions():
    reactants_stoichiometries = []
    non_constant_products_stoichiometries = []
    # Stoichiometries of reactants involved in the rate law
    for reactant in reaction.getListOfReactants():
        species_id = reactant.getSpecies()
        species = model.getSpecies(species_id)
        if species.getId() in rate_law_species:
            stoichiometry = reactant.getStoichiometry()
            reactants_stoichiometries.append(stoichiometry)

    # Stoichiometries of products that are not constant
    for product in reaction.getListOfProducts():
        species_id = product.getSpecies()
        species = model.getSpecies(species_id)
        if not species.getConstant():
            stoichiometry = product.getStoichiometry()
            non_constant_products_stoichiometries.append(stoichiometry)

    stoichiometries_by_reaction.append([reactants_stoichiometries, non_constant_products_stoichiometries])


print(stoichiometries_by_reaction)

def get_stoic(j,k):
    stoi_frac = 0
    add_stoic = 0
    add_stoic_1 = 0
    for i in range(len(stoichiometries_by_reaction[j][0])):
        add_stoic = add_stoic + stoichiometries_by_reaction[j][0][i]
        add_stoic_1 = add_stoic_1 + stoichiometries_by_reaction[j][1][i]
    stoi_frac = (stoichiometries_by_reaction[j][0][k]*add_stoic_1)/(add_stoic)
    return stoi_frac

print(get_stoic(17,1))

for i in range(6000):
    rate_laws = get_rate_law(model)
    for j in range(len(products_by_reaction)):
        for k in range(len(products_by_reaction[j])):
            if non_constant_reaction_products_list[j][k] in species_initial_concentrations:
                species_initial_concentrations[non_constant_reaction_products_list[j][k]] = products_by_reaction[j][k]
            for species_initial_concentrations[j] in rate_law_species:


    for j in Norange(len(rate_laws)):
    # Split the rate law into individual components (species, operators, etc.)
        components = rate_laws[j].split()

        for k in range(len(components)):
            component = components[k]
            if component in species_initial_concentrations:
                # If the component is a species ID, replace it with its initial concentration
                initial_concentration = species_initial_concentrations[component]
                components[k] = str(initial_concentration) if initial_concentration is not None else component
            elif  component.strip('()') in species_initial_concentrations:
                initial_concentration = species_initial_concentrations[component.strip('()')]
                list_a = list(component.strip('()'))
                list_b = list(component)
                list_c = [item for item in list_b if item not in list_a]
                for l in range(len(list_c)):
                    if list_c[l] == '(':
                        components[k] =  list_c[l] + str(initial_concentration) if initial_concentration is not None else component
                    elif list_c[l] == ')':
                        components[k] =  str(initial_concentration) + list_c[l] if initial_concentration is not None else component
            elif component in parameter_ids:
                # If the component is a parameter ID, replace it with its value
                parameter = model.getParameter(component)
                parameter_value = parameter.getValue()
                components[k] = str(parameter_value) if parameter_value is not None else component
            elif component.strip('()') in parameter_ids:
                # If the component is a parameter ID, replace it with its value
                parameter = model.getParameter(component.strip('()'))
                parameter_value = parameter.getValue()
                list_a = list(component.strip('()'))
                list_b = list(component)
                list_c = [item for item in list_b if item not in list_a]
                components[k] = str(parameter_value)
                for l in range(len(list_c)):
                    if list_c[l] == '(':
                        components[k] =  list_c[l] + components[k]
                    elif list_c[l] == ')':
                        components[k] =  components[k] + list_c[l]
        # Join the components back into a modified rate law
        rate_laws[j] = ' '.join(components)
    for j in range(len(rate_laws)):
        rate_laws[j] = eval(rate_laws[j])
    for j in range(len(products_by_reaction)):
        for k in range(len(products_by_reaction[j])):
            products_by_reaction[j][k] = products_by_reaction[j][k] + rate_laws[j]/(6*10000)


# print(products_by_reaction)
# for i in range(15):
#    for j in range(len(prod_first_initial_concentrations)):
#       prod_first_final_concentrations[j] = 

# product_conc_at_t = []

# # Outer loop to vary the parameter values in the user defined range symmetrically
# # for param_value in parameter_values:
    
        
# #     #Create a RoadRunner model from the SBMl model
# # rr_model = rr.RoadRunner(sbml_file_path)

# #     # Reset the model to its initial state
# # rr_model.resetToOrigin()

#     #Set the parameter value for the current iteration
# model.getParameter(kinetic_parameter_id).setValue(12500)

# # List to store concentrations at each minute for the current parameter value
# concentrations_at_each_minute = []

# #Set the Gillespie integrator
# # rr_model.setIntegrator('gillespie')

#     #Inner loop to iterate and store minute wise concentration of species up to 15 minutes (user can modify the time)
# for minute in range(1,15):
#     # Simulate for 1 minute
#     # results = rr_model.simulate(0, minute + 1, selections=species_list)
#     # #Extract the concentrations at the end of the simulation (t=1min)
#     # conc_t_plus_1 = results[-1][species_list.index(product_id)]
#     # #Store concentrations for the current minute
#     # concentrations_at_each_minute.append(conc_t_plus_1)
#     # #Set the conc as the new initial conditions for the next iteration
#     # for i, species_id in enumerate(species_list):
#     #     rr_model[species_id]= results[-1][i]
#     #     #print(conc_t_plus_1)
#     concentrations=get_initial_conditions(model)
#     for i in range(get_initial_conditions(model).len()):
#         concentrations[i]=

    

# # Get the product conc at t = 60 for the given parameter value
# product_conc_at_t.append(conc_t_plus_1)
# #print(f"Minute: {minute}, Product concentration: {conc_t_plus_1}")

# # Fine the maximum product conc at t=60 mins over the range of parameter values, and the corresponding parameter values
# max_product_conc = max(product_conc_at_t)
# max_param_value = parameter_values[product_conc_at_t.index(max_product_conc)]

# print(max_product_conc)
# print(max_param_value)

# #Plot the results
# plt.plot(parameter_values, product_conc_at_t, label = "Product concentration at t = 15 mins")
# plt.scatter([max_param_value], [max_product_conc], color = 'red', label = "Max concentration")
# plt.xlabel("Parameter value")
# plt.ylabel("Product concentration")
# plt.legend()
# plt.show()
