#!/usr/bin/python3

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://192.168.10.41:8001/VisualCron/json"
username = "emixmonitor"
password = "xoch8vu>aFeedi<Dah2phae*yietai"


def get_token(username, password):
    """Obtém um novo token da API do VisualCron."""
    login_url = f"{BASE_URL}/logon?username={username}&password={password}"
    try:
        response = requests.get(login_url)
        response.raise_for_status()  # Levanta uma exceção para códigos de erro HTTP
        login_body = response.json()
        token = login_body.get('Token')
        return token, None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para obter o token: {e}")
        return None, e
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta do token: {e}")
        return None, e

def get_jobs_list(Token):
    if not Token:
        return None

    url_jobs = f"http://192.168.10.41:8001/VisualCron/text/Job/List?token={Token}&columns=id,active,name"

    try:
        response_jobs = requests.get(url_jobs)
        response_jobs.raise_for_status()
        dados = response_jobs.text.strip()
        lines = dados.split('\n')

        if len(lines) < 2:
            return json.dumps([])

        # Tenta decodificar a primeira linha com utf-8-sig e depois recodificar para utf-8
        try:
            header_line = lines[0].encode('latin-1').decode('utf-8-sig').encode('utf-8').decode('utf-8')
            header = [h.strip() for h in header_line.split(',')]
        except UnicodeDecodeError:
            # Se a decodificação com utf-8-sig falhar, tenta a decodificação padrão
            header = [h.strip() for h in lines[0].split(',')]

        jobs_list = []

        for line in lines[1:]:
            values = [v.strip() for v in line.split(',')]
            if len(header) == len(values):
                job_dict = dict(zip(header,values))
                # Converte valores booleanos de string para boolean
                if 'active' in job_dict:
                    job_dict['active'] = job_dict['active'].lower() == 'true'
                    # Adiciona o job à lista apenas se 'active' for True
                    if job_dict['active']:
                        jobs_list.append(job_dict)
        return jobs_list
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter a lista de jobs: {e}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao obter a lista de jobs: {e}")
        return None


def send_request(method, path, params, data=None):
    """Envia uma requisição para a API do VisualCron."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    try:
        response = requests.request(method, url, headers=headers, params=params, json=data)
        response.raise_for_status()

        if response.status_code >= 200 and response.status_code < 300:
            try:
                return response.json(), None
            except json.JSONDecodeError:
                return response.text, None # Se a resposta não for JSON válida
        else:
            try:
                error_response = response.json()
                return None, error_response.get('message', f"Erro desconhecido, status code: {response.status_code}")
            except json.JSONDecodeError:
                return None, f"Erro desconhecido, status code: {response.status_code}, resposta: {response.text}"
    except requests.exceptions.RequestException as e:
        return None, e

def JobStatus(method, path, params, data=None):
    """Envia uma requisição para a API do VisualCron."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json;charset=utf-8"}
    try:
        response = requests.request(method, url, headers=headers, params=params, json=data)
        #print(f"Encoding da resposta: {response.encoding}")
        response.raise_for_status()

        if response.status_code >= 200 and response.status_code < 300:
            try:
                json_data = response.json()
                #Remover campos de nível superior
                fields_to_remove = [
                    "TriggerDependencies",      "Triggers",             "ResetTriggers",
                    "ResetTriggerDepedency",    "Variables",            "GroupOverride",
                    "Flow",                     "JobLoops",             "Tasks",
                    "StartNotifications",       "CompleteNotifications","ErrorNotifications",
                    "TimeExceptions",           "Conditions",           "TimeOut",
                    "ROISettings",              "Test",                 "ResultOutput",
                    "IsTaskRepository",         "UseRunRandomValue",    "RunRandomValue",
                    "Missed",                   "MissedDate",           "Description",
                    "JobDebugging",             "RunMissed",            "RunOnce",
                    "RemoveAfterExecution",     "RunTasksInOrder",      "NotStartIfRunning",
                    "QueueJobs",                "CreatedBy",            "ModifiedBy",
                    "UniqueRunId",              "JobFolders"
                ]
                for field in fields_to_remove:
                    if field in json_data:
                        del json_data[field]

                # Remover campos específicos de cada item na lista "Tasks"
                task_fields_to_remove = [
                    "StartNotifications",       "TimeOut",                  "CompleteNotifications",    "ErrorNotifications",       "Conditions",
                    "Result",                   "TaskDebugging",            "ConditionsArray",          "Description",              "StoreSTDOut",
                    "StoreSTDErr",              "CodePage",                 "TaskType",                 "Flow",                     "Execute",
                    "ExecuteScript",            "DotNetExecute",            "RemoteExecute",            "Kill",                     "RemoteKill",
                    "AS400Command",             "SendKeys",                 "SQL",                      "SSIS",                     "DTS",
                    "SSISDB",                   "SSRS",                     "TableCopy",                "CopyFile",                 "Archive",
                    "ArchiveCompress",          "ArchiveDecompress",        "SyncFile",                 "FTP",                      "PGP",
                    "PGPEncrypt",               "PGPDecrypt",               "Wait",                     "FileDelete",               "FileRename",
                    "FileRead",                 "FileWrite",                "FileTouch",                "FilesList",                "FolderDelete",
                    "FolderCreate",             "FolderRename",             "JobTaskControl",           "ExportSettings",           "Email",
                    "SSH",                      "SystemLogoff",             "SystemShutdown",           "SystemRestart",            "SystemLock",
                    "SystemUnLock",             "SystemHibernate",          "SystemStandby",            "SystemWakeUp",             "SystemWakeUpOnLan",
                    "SystemControlMonitor",     "ServiceStart",             "ServiceRestart",           "ServiceStop",              "VariableSet",
                    "VariableRemove",           "VariableCalculate",        "PrintDocument",            "NetPing",                  "DesktopMacro",
                    "Robot",                    "PlaySound",                "Registry",                 "OfficeMacro",              "XMLCreateNode",
                    "XMLReadNode",              "XMLEditNode",              "XMLDeleteNode",            "XMLTransform",             "XMLValidate",
                    "XMLSign",                  "XMLVerify",                "InstantMessaging",         "ADCreateGroup",            "ADCreateObject",
                    "ADCreateUser",             "ADDeleteObject",           "ADGetGroupMembers",        "ADGetObjectPath",          "ADGetObjectProperty",
                    "ADListObjectPaths",        "ADModifyGroup",            "ADModifyUser",             "ADMoveObject",             "ADRenameObject",
                    "ADSetObjectProperty",      "HTTP",                     "Telnet",                   "RSH",                      "RLogin",
                    "RExec",                    "CheckPort",                "SerialSend",               "WebMacro",                 "ExchangeCreateObject",
                    "ExchangeDeleteObject",     "ExchangeDeleteObjects",    "ExchangeModifyObject",     "ExchangeGetObjects",       "AssemblyExecute",
                    "WebService",               "SNMPGet",                  "SNMPGetNext",              "SNMPGetBulk",              "SNMPSet",
                    "SNMPWalk",                 "WebDAVListItems",          "WebDAVListFolders",        "WebDAVCreateFolder",       "WebDAVDownload",
                    "WebDAVUpload",             "WebDAVDelete",             "WebDAVCopyFiles",          "EventLogRead",             "EventLogWrite",
                    "ExcelGetCell",             "ExcelSetCell",             "ExcelConvert",             "ExcelRecalculate",         "ExcelGetRowCount",
                    "ExcelCreate",              "FileConcatenate",          "PowerShell",               "CloudUploadFiles",         "CloudDownloadFiles",
                    "CloudDeleteItems",         "CloudCreateFolder",        "CloudListItems",           "CloudSyncFiles",           "CloudListFolders",
                    "CloudCopyMoveItems",       "EncryptFilesSymmetric",    "DecryptFilesSymmetric",    "EncryptFilesAsymmetric",   "DecryptFilesAsymmetric",
                    "WindowsUpdate",            "SystemRestoreCreate",      "SystemRestoreDelete",      "SystemRestoreList",        "SystemRestoreRestore",
                    "UnmanagedDLLExecute",      "Popup",                    "SharepointGetLists",       "SharepointCreateList",     "SharepointDeleteList",
                    "SharepointUpdateList",     "SharepointDescribeList",   "SharepointAddListItem",    "SharepointDeleteListItem", "SharepointUpdateListItem",
                    "SharepointGetListItems",   "SharepointUploadFiles",    "SharepointDownloadFiles",  "SharepointListFiles",      "SharepointDeleteFiles",
                    "JobReport",                "XendApp",                  "CrystalReports",           "VirtualServerList",        "VirtualServerStart",
                    "VirtualServerTurnOff",     "VirtualServerSaveState",   "VirtualServerReset",       "VirtualServerPause",       "VirtualServerCheck",
                    "HyperVList",               "HyperVStart",              "HyperVStop",               "HyperVPause",              "HyperVSuspend",
                    "HyperVResume",             "HyperVCheck",              "HyperVReset",              "HyperVCreateSnapshot",     "HyperVApplySnapshot",
                    "HyperVDeleteSnapshot",     "SysLog",                   "VMWareStartVM",            "VMWareStopVM",             "VMWareSuspendVM",
                    "VMWarePauseVM",            "VMWareResumeVM",           "VMWareResetVM",            "VMWareCheckVMStatus",      "VMWareCreateVMSnapshot",
                    "VMWareRevertToVMSnapshot", "VMWareDeleteVMSnapshot",   "VMWareListVMSnapshots",    "VMWareDeleteVM",           "VMWareCloneVM",
                    "VMWareInstallToolsVM",     "VMWareRegisterVM",         "VMWareUnRegisterVM",       "VMWareListVM",             "VMWareGuestCaptureScreen",
                    "VMWareGuestCopyFile",      "VMWareGuestRenameFile",    "VMWareGuestDeleteFile",    "VMWareGuestDirectoryExists","VMWareGuestFileExists",
                    "VMWareGuestDeleteDirectory","VMWareGuestCreateDirectory","VMWareGuestCreateTempFile","VMWareGuestRunCommand",  "VMWareGuestOpenURL",
                    "VMWareGuestKillProcess",   "VMWareGuestListProcesses", "DynamicsCRMCreateEntity",  "DynamicsCRMDeleteEntity",  "DynamicsCRMDownloadAttachment",
                    "DynamicsCRMGetAuditData",  "DynamicsCRMGetEntity",     "DynamicsCRMListEntity",    "DynamicsCRMSetAuditStatus","DynamicsCRMStartWorkflow",
                    "DynamicsCRMUpdateEntity",  "DynamicsCRMUploadAttachment","DynamicsCRMDeleteAttachments","GetChecksum",         "SetAttributes",
                    "ChangeOwner",              "FileSetPermissions",       "FolderSetPermissions",     "FolderList",               "Base64Encode",
                    "Base64Decode",             "ProcessorsAffinity",       "EC2StartInstance",         "EC2LaunchInstance",        "EC2StopInstance",
                    "EC2TerminateInstance",     "EC2RebootInstance",        "EC2ListInstances",         "EC2ListSecurityGroup",     "EC2CreateSecurityGroup",
                    "EC2DeleteSecurityGroup",   "EC2AuthorizeSecurityGroup","EC2RevokeSecurityGroup",   "EC2ListAddress",           "EC2AllocateAddress",
                    "EC2ReleaseAddress",        "EC2AssociateAddress",      "EC2DisassociateAddress",   "EC2ListVolumes",           "EC2DetachVolume",
                    "EC2DeleteVolume",          "EC2AttachVolume",          "EC2CreateVolume",          "EC2ListSnapshots",         "EC2DeleteSnapshots",
                    "EC2CreateSnapshots",       "EC2ListKeyPair",           "EC2DeleteKeyPair",         "EC2CreateKeyPair",         "PDFAddHeaderFooter",
                    "PDFConcatenate",           "PDFConvert",               "PDFSplit",                 "PDFSign",                  "PDFEncrypt",
                    "PDFDecrypt",               "PDFClearSign",             "PDFSetFields",             "PDFGetFields",             "PDFRemovePages",
                    "PDFGetInformation",        "PDFExtract",               "PDFAddAttachments",        "PDFGetAttachments",        "PDFDeleteAttachments",
                    "PDFSearch",                "PDFReplace",               "PDFInsertPages",           "MSMQSendMessage",          "MSMQDeleteMessages",
                    "JobVariableSet",           "AzureStartVM",             "AzureStopVM",              "AzureRestartVM",           "AzureUpdateVM",
                    "AzureCreateVM",            "AzureStartWeb",            "AzureStopWeb",             "AzureRestartWeb",          "AzureRemoveWeb",
                    "AzureCreateWeb",           "Office365GetCalendars",    "Office365AddCalendarEvent","Office365UpdateCalendarEvent","Office365DeleteCalendarEvent",
                    "MSTeamsAddChannelMessage", "AmazonSNSPublishMessage",  "AmazonDynamoDBListTables", "AmazonDynamoDBCreateTable","AmazonDynamoDBUpdateTable",
                    "AmazonDynamoDBDeleteTable","AmazonDynamoDBDescribeTable","AmazonDynamoDBQueryItem","AmazonDynamoDBPutItem",    "AmazonDynamoDBGetItem",
                    "AmazonDynamoDBDeleteItem", "PushbulletSendMessage",    "PushbulletSendLink",       "PushbulletSendFile",       "PushbulletUploadFile",
                    "PushbulletSendSMS",        "SAPRFC",                   "ImageOverlay",             "ImageAdjust",              "ImageCaptureScreen",
                    "ImageConvert",             "ImageCrop",                "ImageFilter",              "ImageFlip",                "ImageJoin",
                    "ImageResize",              "ImageRotate",              "ImageGetEXIFData",         "ImageProfileChange",       "ScanDocument",
                    "ScanDocumentCloud",        "TelegramBotSend",          "TelegramUserSend",         "TwitterTweet",             "TwitterTweetReply",
                    "TwitterGetStatus",         "TwitterDeleteStatus",      "TwitterFollowUser",        "TwitterSendMessage",       "TwitterRetweet",
                    "TwitterLikeTweet",         "TwitterSearchTweets",      "TwitterGetMessages",       "TwitterGetTimeline",       "TwitterGetMentions",
                    "TwitterGetFriends",        "TwitterGetFollowers",      "JSONFilter",               "EnvVariableGet",           "EnvVariableSet",
                    "EnvVariableAppend",        "EnvVariableList",          "EnvVariableDelete",        "EMailGetHeaders",          "EMailGetMessages",
                    "EMailGetSingleMessage",    "EMailDeleteSingleMessage", "EMailDeleteMessages",      "EMailMoveMessages",        "AMQPSendMessage",
                    "SlackSendMessage",         "FacebookPublish",          "IISIsAppPoolExists",       "IISAddApplicationPool",    "IISDeleteApplicationPool",
                    "IISChangeApplicationPoolState","IISAddWebSite",        "IISDeleteWebSite",         "IISAddWebSiteApplication", "IISDeleteWebSiteApplication",
                    "IISAddAppVirtualDirectory","IISDeleteAppVirtualDirectory","IISChangeWebSiteState", "PSProcessSchedule",        "TaskInformaticaRunJob",
                    "PSFindProcesses",          "PSProcessRequest",         "PSProcessReport",          "PSProcessUpdate",          "PSSchedulePSQuery",
                    "PSScheduleBIPublisher",    "PSScheduleConQuery",       "MobileApp",                "IBMCognosRunReport",       "IBMCognosRunJob",
                    "GoogleBigQuery",           "GoogleBigQueryFillTable"
                ]
                # Especifique os campos a serem removidos de Tasks
                if "Tasks" in json_data and isinstance(json_data["Tasks"], list) and task_fields_to_remove:
                    for task in json_data["Tasks"]:
                        for task_field in task_fields_to_remove:
                            if task_field in task:
                                del task[task_field]

                # Converter campos de data para timestamp (focado no nível superior do exemplo)
                date_fields_to_convert = ["DateLastExecution","DateNextExecution","DateLastExited","DateCreated","DateModified"]
                if "Stats" in json_data and isinstance(json_data["Stats"], dict):
                    for field in date_fields_to_convert:
                        if field in json_data["Stats"]:
                            timestamp = convert_date_to_timestamp(json_data["Stats"][field])
                            if timestamp is not None:
                                json_data["Stats"][field] = timestamp

                    date_last_execution_str = json_data["Stats"].get("DateLastExecution")
                    execution_time = json_data["Stats"].get("ExecutionTime")
                    if date_last_execution_str is not None and execution_time is not None:
                        try:
                            date_end_execution_timestamp = int(date_last_execution_str + execution_time)
                            json_data["Stats"]["DateEndExecution"] = date_end_execution_timestamp
                        except TypeError:
                            print("Erro ao somar DateLastExecution e ExecutionTime. Verifique os tipos.")

                return json_data, None
            except json.JSONDecodeError:
                return response.text, None # Se a resposta não for JSON válida
        else:
            try:
                error_response = response.json()
                return None, error_response.get('message', f"Erro desconhecido, status code: {response.status_code}")
            except json.JSONDecodeError:
                return None, f"Erro desconhecido, status code: {response.status_code}, resposta: {response.text}"

    except requests.exceptions.RequestException as e:
        return None, e

def convert_date_to_timestamp(date_string):
    """Converte uma intring de data do formato VisualCron para timestamp Unix"""
    try:
        # Tenta fazer o parsing com informações do timezone
        dt_object = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        timestamp = int(dt_object.timestamp())
        return timestamp
    except ValueError:
        try:
            # Tenta fazer o parsing sem informações de timezone (assume UTC)
            dt_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z")
            timestamp = int(dt_object.timestamp())
            return timestamp
        except ValueError:
            try:
                dt_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
                timestamp = int(dt_object.timestamp())
                return timestamp
            except ValueError:
                print(f"Erro ao converter a data: {date_string}")
                return None

if __name__ == "__main__":

    funcao = sys.argv[1]
    #funcao = "JobStatus"
    #jobid = "d74818d0-614c-447d-9e40-7949c4963ebe"
    #jobid = sys.argv[2]
    jobid = sys.argv[2] if len(sys.argv) > 2 else None

    token, err = get_token(username, password)
    if err:
        print(f"Falha ao obter o token: {err}")
    elif token:
        #print(f"Token obtido: {token}")

        try:
            if funcao == "JobDiscovery":
                arquivo = get_jobs_list(token)
                print(json.dumps(arquivo, indent=4))
            elif funcao == "JobStatus":
                jobs_path = "/Job/Get"
                jobs_params = {"token": token, "id": jobid}
                jobs_data, err = JobStatus("GET", jobs_path, params=jobs_params)
                if err:
                    print(f"Erro ao obter a lista de jobs: {err}")
                elif jobs_data:
                    #print("Lista de Jobs:")
                    print(json.dumps(jobs_data, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"Erro: {e}")
