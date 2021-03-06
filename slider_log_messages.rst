STIX Slider Log Messages
==========================

Use the following table for reference. You can also enable or disable certain
messages using the ``-e`` or ``-d`` flags. Refer to the elevator help
or README for more information on how to handle logging messages.

=================================================================================================================== =========================================================== ====    =====   =================================================================== 
Message                                                                                                             Category                                                    Code    Level   Location                                                            
=================================================================================================================== =========================================================== ====    =====   =================================================================== 
Observable Expressions should not contain placeholders                                                              General                                                     201     Error   ObservableExpressionForElevator.contains_placeholder
Both console and output log have disabled messages                                                                  General                                                     202     Warn    initialize_options
silent option is not compatible with a policy                                                                       General                                                     203     Warn    initialize_options
options not initialized                                                                                             General                                                     204     Warn    set_option_value
No source object exists for [id] to add the relationship [relationship]                                             Possible issue in original STIX 2.0 content                 301     Warn    process_relationships
Unknown hash type [hash_type] used in [id]                                                                          Possible issue in original STIX 2.0 content                 302     Warn    add_hashes_property
[property] is not a legal property in the pattern of [id]                                                           Possible issue in original STIX 2.0 content                 303     Warn    *many* in convert_pattern.py
Unknown address type [type] used in [id]                                                                            Possible issue in original STIX 2.0 content                 304     Warn    convert_addr_pattern
No object [id] is found to add the reference to                                                                     Possible issue in original STIX 2.0 content                 305     Warn    create_references
[cyber_observable_id] is not an index found in [id]                                                                 Possible issue in original STIX 2.0 content                 306     Warn    *many* in convert_cyber_observables.py
No object [id] is found to add the reference to                                                                     Possible issue in original STIX 2.0 content                 307     Warn    create_references        
[id1] is not in this bundle.  Referenced from [id2]                                                                 Possible issue in original STIX 2.0 content                 308     Warn    process_sighting               
[type] in STIX 2.0 has multiple [property], only one is allowed in STIX 1.x. Using first in list - [value] omitted  Multiple values are not supported in STIX 1.x               401     Warn    convert_coa, convert_identity, populate_other_header_fields
Only one dll can be represented in STIX 1.x for [id], using first one - ignoring [value]                            Multiple values are not supported in STIX 1.x               402     Warn    add_process_extension_pattern
The [relationship] relationship between [id1] and [id2] is not supported in STIX 1.x"                               Content not supported in STIX 1.x - Dropping                501     Warn    get_relationship_adder
Multiple File Extensions in [id] not supported yet                                                                  Content not supported in STIX 1.x - Dropping                502     Warn    determine_1x_object_type
[property] not representable in a STIX 1.x [type].  Found in [id]                                                   Content not supported in STIX 1.x - Dropping                503     Warn    convert_image_file_extension
[property] not representable in a STIX 1.x [type].  Found in the pattern of [id]                                    Content not supported in STIX 1.x - Dropping                504     Warn    add_scalar_process_property_pattern,
                                                                                                                                                                                                add_list_process_property_pattern,
                                                                                                                                                                                                add_scalar_registry_key_property_pattern
[op] cannot be converted to a STIX 1.x operator in the pattern of [id]                                              Content not supported in STIX 1.x - Dropping                505     Warn    convert_operator
account_type property of [id] in STIX 2.0 is not directly represented as a property in STIX 1.x                     Content not supported in STIX 1.x - Dropping                506     Warn    convert_user_account_pattern
Received Line [line] in [id] has a prefix that is not representable in STIX 1.x                                     Content not supported in STIX 1.x - Dropping                507     Warn    populate_received_line
Unable to convert STIX 2.0 sighting [id] because it doesn't refer to an indicator                                   Content not supported in STIX 1.x - Dropping                508     Warn    convert_sighting
Cannot convert STIX 2.0 content that contains intrusion-sets                                                        Content not supported in STIX 1.x - Dropping                509     Warn    convert_bundle
Identity has no property to store external-references from [id]                                                     Content not supported in STIX 1.x - Dropping                510     Warn    create_references
pe_type SYS in [id] is valid in STIX 2.0, but not in STIX 1.x                                                       Content not supported in STIX 1.x - Dropping                511     Warn    convert_pe_type
pe_type [pe_type] in [id] is allowed in STIX 2.0, but not in STIX 1.x                                               Content not supported in STIX 1.x - Dropping                512     Warn    convert_pe_type
The [property] property in [id] can refer to any object, so it is not handled yet.                                  STIX slider currently doesn't process this content          601     Warn    add_list_file_property_pattern
number indicies in [id] not handled, yet                                                                            STIX slider currently doesn't process this content          602     Warn    *many* in convert_pattern.py
Unable to determine STIX 1.x type for [id]                                                                          STIX slider currently doesn't process this content          603     Error   convert_cyber_observable
Granular Markings present in [id] are not supported by stix2slider                                                  STIX slider currently doesn't process this content          604     Warn    *many* in convert_stix.py
Source name [name] in external references of [id] not handled, yet                                                  STIX slider currently doesn't process this content          605     Warn    create_references
[property] property in [id] not handled yet                                                                         STIX slider currently doesn't process this content          606     Warn    convert_add_c_o
=================================================================================================================== =========================================================== ====    =====   ===================================================================