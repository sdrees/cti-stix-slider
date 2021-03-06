from functools import cmp_to_key

from cybox.common.environment_variable import (EnvironmentVariable,
                                               EnvironmentVariableList)
from cybox.common.hashes import HashList
from cybox.objects.address_object import Address, EmailAddress
from cybox.objects.archive_file_object import ArchiveFile
from cybox.objects.artifact_object import Artifact
from cybox.objects.as_object import AutonomousSystem
from cybox.objects.domain_name_object import DomainName
from cybox.objects.email_message_object import (Attachments, EmailHeader,
                                                EmailMessage, ReceivedLine,
                                                ReceivedLineList)
from cybox.objects.file_object import File
from cybox.objects.image_file_object import ImageFile
from cybox.objects.mutex_object import Mutex
from cybox.objects.pdf_file_object import (PDFDocumentInformationDictionary,
                                           PDFFile, PDFFileMetadata)
from cybox.objects.process_object import (ArgumentList, ChildPIDList,
                                          ImageInfo, Process)
from cybox.objects.product_object import Product
from cybox.objects.uri_object import URI
from cybox.objects.win_executable_file_object import (Entropy, PEFileHeader,
                                                      PEHeaders,
                                                      PEOptionalHeader,
                                                      PESection,
                                                      PESectionHeaderStruct,
                                                      PESectionList,
                                                      WinExecutableFile)
from cybox.objects.win_file_object import Stream, StreamList, WinFile
from cybox.objects.win_process_object import StartupInfo, WinProcess
from cybox.objects.win_registry_key_object import (RegistryValue,
                                                   RegistryValues,
                                                   WinRegistryKey)
from cybox.objects.win_service_object import ServiceDescriptionList, WinService
from cybox.objects.win_user_object import UserAccount, WinUser
from cybox.objects.x509_certificate_object import (RSAPublicKey,
                                                   SubjectPublicKey, Validity,
                                                   X509Cert, X509Certificate,
                                                   X509V3Extensions)

from stix2slider.common import (AUTONOMOUS_SYSTEM_MAP, DIRECTORY_MAP,
                                EMAIL_MESSAGE_MAP, FILE_MAP,
                                IMAGE_FILE_EXTENSION_MAP,
                                OTHER_EMAIL_HEADERS_MAP,
                                PDF_DOCUMENT_INFORMATION_DICT_MAP,
                                PE_BINARY_FILE_HEADER_MAP,
                                PE_BINARY_OPTIONAL_HEADER_MAP, PROCESS_MAP,
                                REGISTRY_KEY_MAP, REGISTRY_VALUE_MAP,
                                STARTUP_INFO_MAP, USER_ACCOUNT_MAP,
                                WINDOWS_PROCESS_EXTENSION_MAP,
                                WINDOWS_SERVICE_EXTENSION_MAP,
                                X509_CERTIFICATE_MAP,
                                X509_V3_EXTENSIONS_TYPE_MAP, convert_pe_type)
from stix2slider.options import error, warn

_EXTENSIONS_MAP = {
    "archive-ext": ArchiveFile,
    "ntfs-ext": WinFile,
    "pdf-ext": PDFFile,
    "raster-image-ext": ImageFile,
    "windows-pebinary-ext": WinExecutableFile,
    "windows-process-ext": WinProcess,
    "windows-service-ext": WinService,
    # "unix-account_ext": UserAccount
}

_STIX1X_OBJS = {}


def sort_objects_into_processing_order(objs):
    tuple_list = [(k, v) for k, v in objs.items()]
    return sorted(tuple_list, key=lambda x: x[0])


def determine_1x_object_type(c_o_object):
    basic_type = c_o_object["type"]
    if basic_type in ["file"]:
        if "extensions" in c_o_object:
            extensions = list(c_o_object["extensions"].keys())
            if len(extensions) == 1:
                return _EXTENSIONS_MAP[extensions[0]]
            else:
                pass
                warn("Multiple File extensions in %s not supported yet", 502, c_o_object["id"])
        else:
            return File
    if basic_type in ["process"]:
        if "extensions" in c_o_object:
            extensions = list(c_o_object["extensions"].keys())
            object_type_1x = None
            for e in extensions:
                if e == "windows-service-ext":
                    return WinService
                if e == "windows-process-ext":
                    object_type_1x = WinProcess
            if object_type_1x:
                return object_type_1x
        else:
            return Process
    if basic_type in ["user-account"]:
        if "extensions" in c_o_object:
            # extensions = list(c_o_object["extensions"].keys())
            # only one extension is defined, for UNIX, which is cover by the basic user account in STIX 1.x
            return UserAccount
        else:
            if "account_type" in c_o_object:
                if c_o_object["account_type"] in ["windows-local", "windows-domain"]:
                    return WinUser
        # otherwise
        return UserAccount
    if basic_type in ["artifact"]:
        return Artifact
    if basic_type in ["autonomous-system"]:
        return AutonomousSystem
    if basic_type in ["directory"]:
        return File
    if basic_type in ["domain-name"]:
        return DomainName
    if basic_type in ["email-message"]:
        return EmailMessage
    if basic_type in ['ipv4-addr', 'ipv6-addr', 'mac-addr']:
        return Address
    if basic_type in ['email-addr']:
        return EmailAddress
    if basic_type in ['mutex']:
        return Mutex
    if basic_type in ['software']:
        return Product
    if basic_type in ['url']:
        return URI
    if basic_type in ['windows-registry-key']:
        return WinRegistryKey
    if basic_type in ['x509-certificate']:
        return X509Certificate


def convert_obj(obj20, obj1x, mapping_table, obs20_id):
    for key, value in obj20.items():
        if key in mapping_table:
            mapping_table[key].__set__(obj1x, value)
        # else:
        #    warn("%s property in %s is not not representable in STIX 1.x", 0, key, obs20_id)


def add_hashes_property(obj, hash_type, value):
    if hash_type == "MD5":
        obj.md5 = value
    elif hash_type == "SHA-1":
        obj.sha1 = value
    elif hash_type == "SHA-224":
        obj.sha224 = value
    elif hash_type == "SHA-256":
        obj.sha256 = value
    elif hash_type == "SHA-384":
        obj.sha384 = value
    elif hash_type == "SHA-512":
        obj.sha512 = value
    else:
        warn("Unknown hash type %s used in %s", 302, hash_type, obj.id_)


def convert_artifact_c_o(art20, art1x, obs20_id):
    if "mime_type" in art20:
        art1x.content_type = art20["mime_type"]
    if "payload_bin" in art20:
        art1x.packed_data = art20["payload_bin"]
    if "url" in art20:
        pass
        # warn - in STIX 1.x, but not python-stix???
    if "hashes" in art20:
        art1x.hashes = HashList()
        for k, v in art20["hashes"].items():
            add_hashes_property(art1x.hashes, k, v)
    # art1x.packaging.encoding.algorithm = "Base64"


def convert_autonomous_system_c_o(as20, as1x, obs20_id):
    convert_obj(as20, as1x, AUTONOMOUS_SYSTEM_MAP, obs20_id)


def convert_domain_name_c_o(dn20, dn1x):
    dn1x.value = dn20["value"]
    dn1x.type_ = "FQDN"
    # TODO: warn no resolves_to in STIX 1.x


def convert_archive_file_extension(archive_ext, file1x, obs20_id):
    if "version" in archive_ext:
        file1x.version = archive_ext["version"]
    if "comment" in archive_ext:
        file1x.comment = archive_ext["comment"]
    for ref in archive_ext["contains_refs"]:
        if ref in _STIX1X_OBJS:
            file1x.archived_file.append(_STIX1X_OBJS[ref])


def convert_pdf_file_extension(pdf_ext, file1x, obs20_id):
    # TODO: pdfid0, pdfid1
    if "version" in pdf_ext:
        file1x.version = pdf_ext["version"]
    if "is_optimized" in pdf_ext or "document_info_dict" in pdf_ext:
        file1x.metadata = PDFFileMetadata()
        if "is_optimized" in pdf_ext:
            file1x.metadata.optimized = pdf_ext["is_optimized"]
        if "document_info_dict" in pdf_ext:
            file1x.metadata.document_information_dictionary = PDFDocumentInformationDictionary()
            convert_obj(pdf_ext["document_info_dict"],
                        file1x.metadata.document_information_dictionary,
                        PDF_DOCUMENT_INFORMATION_DICT_MAP,
                        obs20_id)


def convert_image_file_extension(image_ext, file1x, obs20_id):
    # TODO: should file1x.is_compressed be populated if there is a compression algorithm?
    # TODO: can image_file_format be determined from the exif property??
    # TODO: exif dictionary
    convert_obj(image_ext, file1x, IMAGE_FILE_EXTENSION_MAP, obs20_id)
    if "exif_tags" in image_ext:
        warn("%s not representable in a STIX 1.x %s.  Found in %s", 503,
             "exif_tags",
             "ImageFile",
             obs20_id)


def convert_windows_pe_binary_file_extension(pe_bin_ext, file1x, obs20_id):
    # TODO: imphash
    # TODO: number_of_sections
    if "pe_type" in pe_bin_ext:
        file1x.type_ = convert_pe_type(pe_bin_ext["pe_type"], obs20_id)
    if not file1x.headers:
        file1x.headers = PEHeaders()
    if any(x in pe_bin_ext for x in ("machine_hex", "time_date_stamp",
                                     "pointer_to_symbol_table_hex",
                                     "number_of_symbols",
                                     "size_of_optional_header",
                                     "characteristics_hex",
                                     "file_header_hashes")
           ):
        file1x.headers.file_header = PEFileHeader()
        convert_obj(pe_bin_ext, file1x.headers.file_header, PE_BINARY_FILE_HEADER_MAP, obs20_id)
    if "file_header_hashes" in pe_bin_ext:
        file1x.headers.file_header.hashes = HashList()
        for k, v in sort_objects_into_processing_order(pe_bin_ext["file_header_hashes"]):
            add_hashes_property(file1x.headers.file_header.hashes, k, v)
    if "optional_header" in pe_bin_ext:
        op_header20 = pe_bin_ext["optional_header"]
        file1x.headers.optional_header = PEOptionalHeader()
        convert_obj(op_header20, file1x.headers.optional_header, PE_BINARY_OPTIONAL_HEADER_MAP, obs20_id)
        if "hashes" in op_header20:
            file1x.headers.optional_header.hashes = HashList()
            for k, v in sort_objects_into_processing_order(op_header20["hashes"]):
                add_hashes_property(file1x.headers.optional_header.hashes, k, v)
    if "sections" in pe_bin_ext:
        file1x.sections = PESectionList()
        for s in pe_bin_ext["sections"]:
            section = PESection()
            file1x.sections.section.append(section)
            if "name" in s or "size" in s:
                section.section_header = PESectionHeaderStruct()
                if "name" in s:
                    section.section_header.name = s["name"]
                if "size" in s:
                    section.section_header.size_of_raw_data = s["size"]
            if "entropy" in s:
                section.entropy = Entropy()
                section.entropy.value = s["entropy"]
            if "hashes" in s:
                section.data_hashes = HashList()
                for k, v in sort_objects_into_processing_order(s["hashes"]):
                    add_hashes_property(section.data_hashes, k, v)


def convert_ntfs_file_extension(ntfs_ext, file1x, obs20_id):
    if "sid" in ntfs_ext:
        file1x.security_id = ntfs_ext["sid"]
    if "alternate_data_streams" in ntfs_ext:
        file1x.stream_list = StreamList()
        ads_list = ntfs_ext["alternate_data_streams"]
        for ads20 in ads_list:
            ads1x = Stream()
            if "name" in ads20:
                ads1x.name = ads20["name"]
            if "size" in ads20:
                ads1x.size_in_bytes = ads20["size"]
            if "hashes" in ads20:
                for k, v in sort_objects_into_processing_order(ads20["hashes"]):
                    add_hashes_property(ads1x, k, v)
            file1x.stream_list.append(ads1x)


def convert_file_extensions(file20, file1x, obs20_id):
    extensions = file20["extensions"]
    if "archive-ext" in extensions:
        convert_archive_file_extension(extensions["archive-ext"], file1x, obs20_id)
    if "pdf-ext" in extensions:
        convert_pdf_file_extension(extensions["pdf-ext"], file1x, obs20_id)
    if "ntfs-ext" in extensions:
        convert_ntfs_file_extension(extensions["ntfs-ext"], file1x, obs20_id)
    if "raster-image-ext" in extensions:
        convert_image_file_extension(extensions["raster-image-ext"], file1x, obs20_id)
    if "windows-pebinary-ext" in extensions:
        convert_windows_pe_binary_file_extension(extensions["windows-pebinary-ext"], file1x, obs20_id)


def convert_file_c_o(file20, file1x, obs20_id):
    # TODO contains_refs
    if "hashes" in file20:
        for k, v in sort_objects_into_processing_order(file20["hashes"]):
            add_hashes_property(file1x, k, v)
    convert_obj(file20, file1x, FILE_MAP, obs20_id)
    if "parent_directory_ref" in file20:
        if file20["parent_directory_ref"] in _STIX1X_OBJS:
            directory_object = _STIX1X_OBJS[file20["parent_directory_ref"]]
            # TODO separator?
            file1x.full_path = str(directory_object.full_path) + "/" + file20["name"]
    # TODO: is_encrypted
    if "extensions" in file20:
        convert_file_extensions(file20, file1x, obs20_id)


def convert_directory_c_o(directory20, file1x, obs20_id):
    convert_obj(directory20, file1x, DIRECTORY_MAP, obs20_id)


def populate_received_line(rl20, rl1x, obs20_id):
    # do we need to consider case?
    # can't there be multiple lines with the same prefix??
    if rl20.startswith("from"):
        rl1x.from_ = rl20
    elif rl20.startswith("by"):
        rl1x.by = rl20
    elif rl20.startswith("via"):
        rl1x.via = rl20
    elif rl20.startswith("with"):
        rl1x.with_ = rl20
    elif rl20.startswith("for"):
        rl1x.for_ = rl20
    elif rl20.startswith("id"):
        rl1x.id_ = rl20
    elif rl20.startswith("timestamp"):
        rl1x.timestamp = rl20
    else:
        warn("Received Line %s in %s has a prefix that is not representable in STIX 1.x", 507, rl20), obs20_id


def populate_other_header_fields(headers20, header1x, obs20_id):
    # keys must match the ones from RFC 2822
    for k, v in headers20.items():
        if isinstance(v, list):
            v = v[0]
            if len(v) > 1:
                for h in v[1:]:
                    warn("%s in STIX 2.0 has multiple %s, only one is allowed in STIX 1.x. Using first in list - %s omitted",
                         401,
                         obs20_id, k, h)
        convert_obj(headers20, header1x, OTHER_EMAIL_HEADERS_MAP, obs20_id)


def convert_email_message_c_o(em20, em1x, obs20_id):
    em1x.header = EmailHeader()
    convert_obj(em20, em1x, EMAIL_MESSAGE_MAP, obs20_id)
    # TODO: is_multipart
    if "from_ref" in em20:
        if em20["from_ref"] in _STIX1X_OBJS:
            em1x.header.from_ = _STIX1X_OBJS[em20["from_ref"]]
        else:
            warn("%s is not an index found in %s", 306, em20["from_ref"], obs20_id)
    if "sender_ref" in em20:
        if em20["sender_ref"] in _STIX1X_OBJS:
            em1x.header.sender = _STIX1X_OBJS[em20["sender_ref"]]
        else:
            warn("%s ia not an index found in %s", 306, em20["sender_ref"], obs20_id)
    if "to_refs" in em20:
        to_address_objects = []
        for to_ref in em20["to_refs"]:
            if to_ref in _STIX1X_OBJS:
                to_address_objects.append(_STIX1X_OBJS[to_ref])
                em1x.header.to = to_address_objects
            else:
                warn("%s ia not an index found in %s", 306, to_ref, obs20_id)
    if "cc_refs" in em20:
        cc_address_objects = []
        for cc_ref in em20["cc_refs"]:
            if cc_ref in _STIX1X_OBJS:
                cc_address_objects.append(_STIX1X_OBJS[cc_ref])
                em1x.header.cc = cc_address_objects
            else:
                warn("%s ia not an index found in %s", 306, cc_ref, obs20_id)
    if "bcc_refs" in em20:
        bcc_address_objects = []
        for bcc_ref in em20["bcc_refs"]:
            if bcc_ref in _STIX1X_OBJS:
                bcc_address_objects.append(_STIX1X_OBJS[bcc_ref])
                em1x.header.bcc = bcc_address_objects
            else:
                warn("%s ia not an index found in %s", 306, bcc_ref, obs20_id)
    if "content_type" in em20:
        em1x.header.content_type = em20["content_type"]
    if "received_lines" in em20:
        em1x.header.received_lines = ReceivedLineList()
        for rl20 in em20["received_lines"]:
            rl1x = ReceivedLine()
            em1x.header.received_lines.append(rl1x)
            populate_received_line(rl20, rl1x, obs20_id)
    if "additional_header_fields" in em20:
        populate_other_header_fields(em20["additional_header_fields"], em1x.header, obs20_id)
    # TODO: additional_header_fields  (in_reply_to, message_id, reply_to, errors_to, ...?
    if "body_multipart" in em20:
        attachments = []
        for part in em20["body_multipart"]:
            # TODO: content_disposition is optional, so we can't depend upon it
            # if "content_disposition" in part and part["content_disposition"].find("attachment"):
            if "body_raw_ref" in part:
                if part["body_raw_ref"] in _STIX1X_OBJS:
                    obj = _STIX1X_OBJS[part["body_raw_ref"]]
                    # TODO: can we handle other object/content types?
                    if isinstance(obj, File):
                        attachments.append(obj)
                else:
                    warn("%s ia not an index found in %s", 306, part["body_raw_ref"], obs20_id)
        if attachments:
            em1x.attachments = Attachments()
            for a in attachments:
                em1x.add_related(a, "Contains", inline=True)
                em1x.attachments.append(a.parent.id_)
    # TODO raw_email_refs


def convert_addr_c_o(addr20, addr1x, obs20_id):
    if addr20["type"] == 'ipv4-addr':
        addr1x.category = Address.CAT_IPV4
    elif addr20["type"] == 'ipv6-addr':
        addr1x.category = Address.CAT_IPV6
    elif addr20["type"] == 'mac-addr':
        addr1x.category = Address.CAT_MAC
    if "resolves_to_refs" in addr20:
        for ref in addr20["resolves_to_refs"]:
            if ref in _STIX1X_OBJS:
                obj = _STIX1X_OBJS[ref]
                addr1x.add_related(obj, "Resolved_To", inline=True)
            else:
                warn("%s ia not an index found in %s", 306, ref, obs20_id)
    if "belongs_to_refs" in addr20:
        warn("%s property in %s not handled yet", 606, "belongs_to_refs", obs20_id)


def convert_process_extensions(process20, process1x, obs20_id):
    extensions = process20["extensions"]
    if "windows-process-ext" in extensions:
        windows_process = extensions["windows-process-ext"]
        convert_obj(windows_process, process1x, WINDOWS_PROCESS_EXTENSION_MAP, obs20_id)
        if "startup_info" in windows_process:
            process1x.startup_info = StartupInfo()
            convert_obj(windows_process["startup_info"], process1x.startup_info, STARTUP_INFO_MAP)
    if "windows-service-ext" in extensions:
        windows_service = extensions["windows-service-ext"]
        convert_obj(windows_service, process1x, WINDOWS_SERVICE_EXTENSION_MAP, obs20_id)
        if "service_dll_refs" in windows_service:
            if windows_service["service_dll_refs"][0] in _STIX1X_OBJS:
                file_object = _STIX1X_OBJS[windows_service["service_dll_refs"][0]]
                if "name" in file_object:
                    process1x.service_dll = file_object.file_name
            if len(windows_service["service_dll_refs"]) > 1:
                for dll_ref in windows_service["service_dll_refs"][1:]:
                    warn("%s in STIX 2.0 has multiple %s, only one is allowed in STIX 1.x. Using first in list - %s omitted",
                         401,
                         obs20_id, "service_dll_refs", dll_ref)
        if "descriptions" in windows_service:
            process1x.descriptions = ServiceDescriptionList()
            # TODO:  is this they way to make this assignment?
            process1x.descriptions.description = windows_service["descriptions"]


def convert_process_c_o(process20, process1x, obs20_id):
    convert_obj(process20, process1x, PROCESS_MAP, obs20_id)
    if "cwd" in process20:
        if not process1x.image_info:
            process1x.image_info = ImageInfo()
        process1x.image_info.current_directory = process20["cwd"]
    if "arguments" in process20:
        process1x.argument_list = ArgumentList()
        for a in process20["arguments"]:
            process1x.argument_list.append(a)
    if "command_line" in process20:
        if not process1x.image_info:
            process1x.image_info = ImageInfo()
        process1x.image_info.command_line = process20["command_line"]
    if "environment_variables" in process20:
        process1x.environment_variable_list = EnvironmentVariableList()
        for k, v in process20["environment_variables"].items():
            ev = EnvironmentVariable()
            process1x.environment_variable_list.append(ev)
            ev.name = k
            ev.value = v
    if "opened_connection_ref" in process20:
        # TODO
        pass
    if "creator_user_ref" in process20:
        if process20["creator_user_ref"] in _STIX1X_OBJS:
            account_object = _STIX1X_OBJS[process20["creator_user_ref"]]
            if "account_login" in account_object:
                process1x.username = account_object.username
    if "binary_ref" in process20:
        # TODO: should this be a reference to related observable
        if process20["binary_ref"] in _STIX1X_OBJS:
            file_obj = _STIX1X_OBJS[process20["binary_ref"]]
            if file_obj.file_name:
                if not process1x.image_info:
                    process1x.image_info = ImageInfo()
                process1x.image_info.file_name = file_obj.file_name
                # TODO: file_obj.full_path
            # TODO: other properties - some not representable
    if "parent_ref" in process20:
        if process20["parent_ref"] in _STIX1X_OBJS:
            process_object = _STIX1X_OBJS[process20["parent_ref"]]
            if "pid" in process_object:
                process1x.parent_pid = process_object.pid
    if "child_refs" in process20:
        process1x.child_pid_list = ChildPIDList()
        for cr in process20["child_refs"]:
            process_object = _STIX1X_OBJS[cr]
            if "pid" in process_object:
                process1x.child_pid_list.append(process_object.pid)
    if "extensions" in process20:
        convert_process_extensions(process20, process1x, obs20_id)


def convert_software_c_o(soft20, prod1x, obs20_id):
    prod1x.product = soft20["name"]
    # TODO: cpe
    if "languages" in soft20:
        prod1x.language = soft20["languages"][0]
        if len(soft20["languages"]) > 1:
            for l in soft20["languages"][1:]:
                warn("%s in STIX 2.0 has multiple %s, only one is allowed in STIX 1.x. Using first in list - %s omitted",
                     401, obs20_id, "languages", l)

    if "vendor" in soft20:
        prod1x.vendor = soft20["vendor"]
    if "version" in soft20:
        prod1x.version = soft20["version"]


def convert_unix_account_extensions(ua20, ua1x, obs20_id):
    if "extensions" in ua20:
        # must be unix-account-ext
        unix_account_ext = ua20["extensions"]["unix-account-ext"]
        # TODO: gid
        # TODO: groups
        if "home_dir" in unix_account_ext:
            ua1x.home_directory = unix_account_ext["home_dir"]
        # TODO: shell


def convert_user_account_c_o(ua20, ua1x, obs20_id):
    convert_obj(ua20, ua1x, USER_ACCOUNT_MAP, obs20_id)
    convert_unix_account_extensions(ua20, ua1x, obs20_id)


def convert_window_registry_value(v20, obs20_id):
    v1x = RegistryValue()
    convert_obj(v20, v1x, REGISTRY_VALUE_MAP, obs20_id)
    return v1x


def convert_windows_registry_key_c_o(wrk20, wrk1x, obs20_id):
    convert_obj(wrk20, wrk1x, REGISTRY_KEY_MAP, obs20_id)
    if "values" in wrk20:
        values = []
        for v in wrk20["values"]:
            values.append(convert_window_registry_value(v, obs20_id))
        wrk1x.values = RegistryValues()
        wrk1x.values.value = values
    if "creator_user_ref" in wrk20:
        if wrk20["creator_user_ref"] in _STIX1X_OBJS:
            account_object = _STIX1X_OBJS[wrk20["creator_user_ref"]]
            wrk1x.creator_username = account_object.username


def convert_subfield(obj, rhs_value, property, sub_object_class, setting_function):
    sub_object = getattr(obj, property)
    if not sub_object:
        sub_object = sub_object_class()
        setattr(obj, property, sub_object)
    setting_function.__set__(sub_object, rhs_value)


def convert_x509_certificate_c_o(c_o_object, obj1x, obs20_id):
    obj1x.certificate = X509Cert()
    convert_obj(c_o_object, obj1x.certificate, X509_CERTIFICATE_MAP, obs20_id)
    if "validity_not_before" in c_o_object or "validity_not_after" in c_o_object:
        obj1x.certificate.validity = Validity()
        if "validity_not_before" in c_o_object:
            obj1x.certificate.validity.not_before = c_o_object["validity_not_before"]
        if "validity_not_after" in c_o_object:
            obj1x.certificate.validity.not_after = c_o_object["validity_not_after"]
    if ("subject_public_key_algorithm" in c_o_object or
            "subject_public_key_modulus" in c_o_object or
            "subject_public_key_exponent" in c_o_object):
        obj1x.certificate.subject_public_key = SubjectPublicKey()
        if "subject_public_key_algorithm" in c_o_object:
            obj1x.certificate.subject_public_key.public_key_algorithm = c_o_object["subject_public_key_algorithm"]
        if "subject_public_key_modulus" in c_o_object or "subject_public_key_exponent" in c_o_object:
            obj1x.certificate.subject_public_key.rsa_public_key = RSAPublicKey()
            if "subject_public_key_modulus" in c_o_object:
                obj1x.certificate.subject_public_key.rsa_public_key.modulus = c_o_object["subject_public_key_modulus"]
            if "subject_public_key_exponent" in c_o_object:
                obj1x.certificate.subject_public_key.rsa_public_key.exponent = c_o_object["subject_public_key_exponent"]
    if "x509_v3_extensions" in c_o_object:
        v3_ext = c_o_object["x509_v3_extensions"]
        obj1x.certificate.standard_extensions = X509V3Extensions()
        convert_obj(v3_ext, obj1x.certificate.standard_extensions, X509_V3_EXTENSIONS_TYPE_MAP, obs20_id)


def convert_cyber_observable(c_o_object, obs20_id):
    type1x = determine_1x_object_type(c_o_object)
    if type1x:
        obj1x = type1x()
    else:
        error("Unable to determine STIX 1.x type for %s", 603, obs20_id)
    type_name20 = c_o_object["type"]
    if type_name20 == "artifact":
        convert_artifact_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "autonomous-system":
        convert_autonomous_system_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "directory":
        convert_directory_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "domain_name":
        convert_domain_name_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "email-message":
        convert_email_message_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "file":
        convert_file_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 in ['ipv4-addr', 'ipv6-addr', 'mac-addr', 'email-addr']:
        # TODO: email_address have display_name property
        obj1x.address_value = c_o_object["value"]
        convert_addr_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "mutex":
        obj1x.name = c_o_object["name"]
        obj1x.named = True
    elif type_name20 == "process":
        convert_process_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == 'software':
        convert_software_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "url":
        obj1x.value = c_o_object["value"]
        obj1x.type_ = URI.TYPE_URL
    elif type_name20 == "user-account":
        convert_user_account_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "windows-registry-key":
        convert_windows_registry_key_c_o(c_o_object, obj1x, obs20_id)
    elif type_name20 == "x509-certificate":
        convert_x509_certificate_c_o(c_o_object, obj1x, obs20_id)
    return obj1x


def get_refs(obj):
    refs = []
    for k, v in obj.items():
        if k.endswith("ref"):
            refs.append(obj[k])
        if k.endswith("refs"):
            refs.extend(obj[k])
    # handle sub-objects
    if "type" in obj:
        if obj["type"] == "email-message" and "body_multipart" in obj:
            for part in obj["body_multipart"]:
                refs.extend(get_refs(part))
        elif obj["type"] == "file" and "extensions" in obj:
            extensions = obj["extensions"]
            if "archive-ext" in extensions:
                refs.extend(extensions["archive-ext"]["contains_refs"])
            # TODO: rest of extensions
    return refs


def process_before(key_obj1, key_obj2):
    # if the key of obj1 is referenced by obj2, obj1 must be processed before
    # if obj1 has no references, then process first
    refs = get_refs(key_obj2[1])
    if refs and key_obj1[0] in refs:
        return -1
    else:
        return 1


def sort_objects_into_obj_processing_order(objs):
    tuple_list = [(k, v) for k, v in objs.items()]
    return sorted(tuple_list, key=cmp_to_key(process_before))


def convert_cyber_observables(c_o_objects, obs20_id):
    global _STIX1X_OBJS
    _STIX1X_OBJS = {}
    sorted_obj = sort_objects_into_obj_processing_order(c_o_objects)
    for tup in sorted_obj:
        _STIX1X_OBJS[tup[0]] = convert_cyber_observable(tup[1], obs20_id)
    # return the parent, so you get related objects
    return _STIX1X_OBJS[sorted_obj[-1][0]].parent
