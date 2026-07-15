# -*- coding: utf-8 -*-

from typing import Dict, Iterable, List, Optional

from ...core.model.Field import Field
from ..adapter.StringAdapter import StringAdapter
from ...core.enum import MetadataFieldKey


class MetadataFields:
    EXIF_FIELDS = {
        MetadataFieldKey.FILE: Field(
            normalized="File",
            core="os",
            label="File",
            attribute="File",
            description="Nome do arquivo de imagem. [File]",
            level=3,
            key=MetadataFieldKey.FILE,
        ),
        MetadataFieldKey.PATH: Field(
            normalized="Path",
            core="os",
            label="Path",
            attribute="Path",
            description="Caminho completo do arquivo de imagem. [Path]",
            level=3,
            key=MetadataFieldKey.PATH,
        ),
        MetadataFieldKey.FORMAT: Field(
            normalized="Format",
            core="os",
            label="Format",
            attribute="FormatMod",
            description="Formato e modo de cor da imagem. [FormatMod]",
            level=3,
            key=MetadataFieldKey.FORMAT,
        ),
        MetadataFieldKey.SIZE_MB: Field(
            normalized="SizeMb",
            core="os",
            label="Size MB",
            attribute="SizeMB",
            description="Tamanho do arquivo em megabytes. [SizeMB]",
            level=3,
            key=MetadataFieldKey.SIZE_MB,
        ),
        MetadataFieldKey.GPS_STATUS_EXIF: Field(
            normalized="EXIF:GPSInfo:GPSStatus",
            core="EXIF",
            label="GPS Status EXIF",
            attribute="GpsStatusExif",
            description="Status do GPS registrado no EXIF (ex: 'A' = Active). [GpsStatusExif]",
            level=3,
            key=MetadataFieldKey.GPS_STATUS_EXIF,
        ),
        MetadataFieldKey.GPS_MAP_DATUM: Field(
            normalized="EXIF:GPSInfo:GPSMapDatum",
            core="EXIF",
            label="GPS Map Datum",
            attribute="GPSDatum",
            description="Datum geodesico usado nas coordenadas GPS. [GPSDatum]",
            level=3,
            key=MetadataFieldKey.GPS_MAP_DATUM,
        ),
        MetadataFieldKey.GPS_VERSION_ID: Field(
            normalized="EXIF:GPSInfo:GPSVersionID",
            core="EXIF",
            label="GPS Version ID",
            attribute="GpsVersionId",
            description="Versao do padrao GPS registrado no EXIF (ex: '2 3 0 0'). [GpsVersionId]",
            level=3,
            key=MetadataFieldKey.GPS_VERSION_ID,
        ),
        MetadataFieldKey.GPS_ALTITUDE_REF: Field(
            normalized="EXIF:GPSInfo:GPSAltitudeRef",
            core="EXIF",
            label="GPS Altitude Ref",
            attribute="GpsAltRef",
            description="Referencia de altitude GPS (0 = nivel do mar / acima, 1 = abaixo). [GpsAltRef]",
            level=3,
            key=MetadataFieldKey.GPS_ALTITUDE_REF,
        ),
        MetadataFieldKey.GPS_ALTITUDE: Field(
            normalized="EXIF:GPSInfo:GPSAltitude",
            core="EXIF",
            label="GPS Altitude",
            attribute="GpsAltitude",
            description="Altitude GPS registrada no EXIF em metros (MSL). [GpsAltitude]",
            level=3,
            key=MetadataFieldKey.GPS_ALTITUDE,
        ),
        MetadataFieldKey.GPS_LATITUDE_REF: Field(
            normalized="EXIF:GPSInfo:GPSLatitudeRef",
            core="EXIF",
            label="GPS Latitude Ref",
            attribute="GpsLatRef",
            description="Referencia de latitude GPS (N/S). [GpsLatRef]",
            level=3,
            key=MetadataFieldKey.GPS_LATITUDE_REF,
        ),
        MetadataFieldKey.GPS_LONGITUDE_REF: Field(
            normalized="EXIF:GPSInfo:GPSLongitudeRef",
            core="EXIF",
            label="GPS Longitude Ref",
            attribute="GpsLongRef",
            description="Referencia de longitude GPS (E/W). [GpsLongRef]",
            level=3,
            key=MetadataFieldKey.GPS_LONGITUDE_REF,
        ),
        MetadataFieldKey.MODEL: Field(
            normalized="EXIF:Model",
            core="EXIF",
            label="Model",
            attribute="Model",
            description="Modelo da camera que capturou a imagem. [Model]",
            level=3,
            key=MetadataFieldKey.MODEL,
        ),
        MetadataFieldKey.SOFTWARE: Field(
            normalized="EXIF:Software",
            core="EXIF",
            label="Software",
            attribute="Firmware",
            description="Software ou firmware gravado no metadado. [Firmware]",
            level=3,
            key=MetadataFieldKey.SOFTWARE,
        ),
        MetadataFieldKey.X_RESOLUTION: Field(
            normalized="EXIF:XResolution",
            core="EXIF",
            label="X Resolution",
            attribute="DPIWidth",
            description="Resolucao horizontal informada no EXIF (DPI). [DPIWidth]",
            level=3,
            key=MetadataFieldKey.X_RESOLUTION,
        ),
        MetadataFieldKey.Y_RESOLUTION: Field(
            normalized="EXIF:YResolution",
            core="EXIF",
            label="Y Resolution",
            attribute="DPIHeight",
            description="Resolucao vertical informada no EXIF (DPI). [DPIHeight]",
            level=3,
            key=MetadataFieldKey.Y_RESOLUTION,
        ),
        MetadataFieldKey.SHUTTER_SPEED_VALUE: Field(
            normalized="EXIF:ShutterSpeedValue",
            core="EXIF",
            label="Shutter Speed Value",
            attribute="ShutterSp",
            description="Velocidade do obturador registrada no EXIF. [ShutterSp]",
            level=3,
            key=MetadataFieldKey.SHUTTER_SPEED_VALUE,
        ),
        MetadataFieldKey.DATE_TIME_ORIGINAL: Field(
            normalized="EXIF:DateTimeOriginal",
            core="EXIF",
            label="Date Time Original",
            attribute="DateTime",
            description="Data e hora original da captura. [DateTime]",
            level=3,
            key=MetadataFieldKey.DATE_TIME_ORIGINAL,
        ),
        MetadataFieldKey.APERTURE_VALUE: Field(
            normalized="EXIF:ApertureValue",
            core="EXIF",
            label="Aperture Value",
            attribute="ApertureV",
            description="Valor de abertura usado na captura. [ApertureV]",
            level=3,
            key=MetadataFieldKey.APERTURE_VALUE,
        ),
        MetadataFieldKey.MAX_APERTURE_VALUE: Field(
            normalized="EXIF:MaxApertureValue",
            core="EXIF",
            label="Max Aperture Value",
            attribute="MaxApertV",
            description="Maior abertura disponivel da lente. [MaxApertV]",
            level=3,
            key=MetadataFieldKey.MAX_APERTURE_VALUE,
        ),
        MetadataFieldKey.LIGHT_SOURCE: Field(
            normalized="EXIF:LightSource",
            core="EXIF",
            label="Light Source",
            attribute="LightSour",
            description="Codigo da fonte de iluminacao da cena. [LightSour]",
            level=3,
            key=MetadataFieldKey.LIGHT_SOURCE,
        ),
        MetadataFieldKey.FOCAL_LENGTH: Field(
            normalized="EXIF:FocalLength",
            core="EXIF",
            label="Focal Length",
            attribute="FocalLeng",
            description="Distancia focal da lente em mm. [FocalLeng]",
            level=3,
            key=MetadataFieldKey.FOCAL_LENGTH,
        ),
        MetadataFieldKey.EXIF_IMAGE_WIDTH: Field(
            normalized="EXIF:ExifImageWidth",
            core="EXIF",
            label="EXIF Image Width",
            attribute="WidthPX",
            description="Largura da imagem em pixels (EXIF). [WidthPX]",
            level=3,
            key=MetadataFieldKey.EXIF_IMAGE_WIDTH,
        ),
        MetadataFieldKey.EXIF_IMAGE_HEIGHT: Field(
            normalized="EXIF:ExifImageHeight",
            core="EXIF",
            label="EXIF Image Height",
            attribute="HeightPX",
            description="Altura da imagem em pixels (EXIF). [HeightPX]",
            level=3,
            key=MetadataFieldKey.EXIF_IMAGE_HEIGHT,
        ),
        MetadataFieldKey.EXPOSURE_TIME: Field(
            normalized="EXIF:ExposureTime",
            core="EXIF",
            label="Exposure Time",
            attribute="ExpTime",
            description="Tempo de abertura do obturador em segundos (ex: 0.001 = 1/1000s). "
            "Valores altos causam motion blur em voo e comprometem alinhamento fotogrametrico. "
            "Recomendado abaixo de 1/500s para mapeamento. [ExpTime]",
            level=3,
            key=MetadataFieldKey.EXPOSURE_TIME,
        ),
        MetadataFieldKey.F_NUMBER: Field(
            normalized="EXIF:FNumber",
            core="EXIF",
            label="F Number",
            attribute="FNumber",
            description="Numero f usado na captura. [FNumber]",
            level=3,
            key=MetadataFieldKey.F_NUMBER,
        ),
        MetadataFieldKey.EXPOSURE_PROGRAM: Field(
            normalized="EXIF:ExposureProgram",
            core="EXIF",
            label="Exposure Program",
            attribute="ExpProg",
            description="Programa de exposicao selecionado pela camera. [ExpProg]",
            level=3,
            key=MetadataFieldKey.EXPOSURE_PROGRAM,
        ),
        MetadataFieldKey.ISO_SPEED_RATINGS: Field(
            normalized="EXIF:ISOSpeedRatings",
            core="EXIF",
            label="ISO Speed Ratings",
            attribute="ISOSpeed",
            description="Sensibilidade ISO usada na captura. [ISOSpeed]",
            level=3,
            key=MetadataFieldKey.ISO_SPEED_RATINGS,
        ),
        MetadataFieldKey.EXPOSURE_MODE: Field(
            normalized="EXIF:ExposureMode",
            core="EXIF",
            label="Exposure Mode",
            attribute="ExpMode",
            description="Modo de exposicao configurado na camera. [ExpMode]",
            level=3,
            key=MetadataFieldKey.EXPOSURE_MODE,
        ),
        MetadataFieldKey.LENS_SPECIFICATION: Field(
            normalized="EXIF:LensSpecification",
            core="EXIF",
            label="Lens Specification",
            attribute="Lens",
            description="Faixa focal e de abertura da lente. [Lens]",
            level=3,
            key=MetadataFieldKey.LENS_SPECIFICATION,
        ),
        MetadataFieldKey.DIGITAL_ZOOM_RATIO: Field(
            normalized="EXIF:DigitalZoomRatio",
            core="EXIF",
            label="Digital Zoom Ratio",
            attribute="ZoomRatio",
            description="Razao de zoom digital aplicada na captura. [ZoomRatio]",
            level=3,
            key=MetadataFieldKey.DIGITAL_ZOOM_RATIO,
        ),
        MetadataFieldKey.EXIF_SHARPNESS: Field(
            normalized="EXIF:Sharpness",
            core="EXIF",
            label="EXIF Sharpness",
            attribute="Sharpness",
            description="Nivel de nitidez da imagem mapeado pelo EXIF. [Sharpness]",
            level=3,
            key=MetadataFieldKey.EXIF_SHARPNESS,
        ),
        MetadataFieldKey.EXIF_CONTRAST: Field(
            normalized="EXIF:Contrast",
            core="EXIF",
            label="EXIF Contrast",
            attribute="Contrast",
            description="Nivel de contraste aplicado na captura. [Contrast]",
            level=3,
            key=MetadataFieldKey.EXIF_CONTRAST,
        ),
        MetadataFieldKey.EXIF_SATURATION: Field(
            normalized="EXIF:Saturation",
            core="EXIF",
            label="EXIF Saturation",
            attribute="Saturation",
            description="Nivel de saturacao de cor da imagem. [Saturation]",
            level=3,
            key=MetadataFieldKey.EXIF_SATURATION,
        ),
        MetadataFieldKey.EXIF_FLASH_PIX_VERSION: Field(
            normalized="EXIF:FlashPixVersion",
            core="EXIF",
            label="EXIF Flash Pix Version",
            attribute="FlashPixVer",
            description="Versao FlashPix gravada no EXIF. [FlashPixVer]",
            level=3,
            key=MetadataFieldKey.EXIF_FLASH_PIX_VERSION,
        ),
        MetadataFieldKey.EXIF_COLOR_SPACE: Field(
            normalized="EXIF:ColorSpace",
            core="EXIF",
            label="EXIF Color Space",
            attribute="ColorSpace",
            description="Espaco de cor utilizado na captura da imagem. [ColorSpace]",
            level=3,
            key=MetadataFieldKey.EXIF_COLOR_SPACE,
        ),
    }

    DJI_XMP_FIELDS = {
        MetadataFieldKey.GPS_STATUS_XMP: Field(
            normalized="xmp_bloco_1:drone-dji:GpsStatus",
            core="xmp_bloco_1",
            label="GPS Status XMP",
            attribute="GpsStatusXmp",
            description="Status do GPS DJI registrado no XMP (ex: 'RTK', 'Normal', 'A'). [GpsStatusXmp]",
            level=3,
            key=MetadataFieldKey.GPS_STATUS_XMP,
        ),
        MetadataFieldKey.ALTITUDE_TYPE: Field(
            normalized="xmp_bloco_1:drone-dji:AltitudeType",
            core="xmp_bloco_1",
            label="Altitude Type",
            attribute="Ytype",
            description="Tipo de altitude registrado pelo drone. [Ytype]",
            level=3,
            key=MetadataFieldKey.ALTITUDE_TYPE,
        ),
        MetadataFieldKey.GPS_LATITUDE: Field(
            normalized="EXIF:GPSInfo:GPSLatitude",
            core="xmp_bloco_1",
            label="GPS Latitude",
            attribute="GpsLat",
            description="Latitude GPS da aeronave na captura (tupla DMS do EXIF). [GpsLat]",
            level=3,
            key=MetadataFieldKey.GPS_LATITUDE,
        ),
        MetadataFieldKey.GPS_LONGITUDE: Field(
            normalized="EXIF:GPSInfo:GPSLongitude",
            core="xmp_bloco_1",
            label="GPS Longitude",
            attribute="GPSLong",
            description="Longitude GPS da aeronave na captura (tupla DMS do EXIF). [GPSLong]",
            level=3,
            key=MetadataFieldKey.GPS_LONGITUDE,
        ),
        MetadataFieldKey.GPS_LATITUDE_XMP: Field(
            normalized="xmp_bloco_1:drone-dji:GPSLatitude",
            core="xmp_bloco_1",
            label="GPS Latitude XMP",
            attribute="GpsLatXmp",
            description="Latitude GPS do XMP DJI em decimal com sinal (ex: -12.21543681). [GpsLatXmp]",
            level=3,
            key=MetadataFieldKey.GPS_LATITUDE_XMP,
        ),
        MetadataFieldKey.GPS_LONGITUDE_XMP: Field(
            normalized="xmp_bloco_1:drone-dji:GPSLongitude",
            core="xmp_bloco_1",
            label="GPS Longitude XMP",
            attribute="GPSLongXmp",
            description="Longitude GPS do XMP DJI em decimal com sinal (ex: -46.60643471). [GPSLongXmp]",
            level=3,
            key=MetadataFieldKey.GPS_LONGITUDE_XMP,
        ),
        MetadataFieldKey.ABSOLUTE_ALTITUDE: Field(
            normalized="xmp_bloco_1:drone-dji:AbsoluteAltitude",
            core="xmp_bloco_1",
            label="Absolute Altitude",
            attribute="AbsZ",
            description="Altitude absoluta da aeronave. [AbsZ]",
            level=3,
            key=MetadataFieldKey.ABSOLUTE_ALTITUDE,
        ),
        MetadataFieldKey.RELATIVE_ALTITUDE: Field(
            normalized="xmp_bloco_1:drone-dji:RelativeAltitude",
            core="xmp_bloco_1",
            label="Relative Altitude",
            attribute="RelativeZ",
            description="Altitude relativa ao ponto de decolagem. [RelativeZ]",
            level=3,
            key=MetadataFieldKey.RELATIVE_ALTITUDE,
        ),
        MetadataFieldKey.GIMBAL_ROLL_DEGREE: Field(
            normalized="xmp_bloco_1:drone-dji:GimbalRollDegree",
            core="xmp_bloco_1",
            label="Gimbal Roll Degree",
            attribute="GimbRoll",
            description="Angulo de rolagem do gimbal em graus. [GimbRoll]",
            level=3,
            key=MetadataFieldKey.GIMBAL_ROLL_DEGREE,
        ),
        MetadataFieldKey.GIMBAL_YAW_DEGREE: Field(
            normalized="xmp_bloco_1:drone-dji:GimbalYawDegree",
            core="xmp_bloco_1",
            label="Gimbal Yaw Degree",
            attribute="GimbYaw",
            description="Angulo de yaw do gimbal em graus. [GimbYaw]",
            level=3,
            key=MetadataFieldKey.GIMBAL_YAW_DEGREE,
        ),
        MetadataFieldKey.GIMBAL_PITCH_DEGREE: Field(
            normalized="xmp_bloco_1:drone-dji:GimbalPitchDegree",
            core="xmp_bloco_1",
            label="Gimbal Pitch Degree",
            attribute="GimbPitch",
            description="Angulo de pitch do gimbal em graus. [GimbPitch]",
            level=3,
            key=MetadataFieldKey.GIMBAL_PITCH_DEGREE,
        ),
        MetadataFieldKey.FLIGHT_ROLL_DEGREE: Field(
            normalized="xmp_bloco_1:drone-dji:FlightRollDegree",
            core="xmp_bloco_1",
            label="Flight Roll Degree",
            attribute="DroneRoll",
            description="Angulo de rolagem da aeronave em graus. [DroneRoll]",
            level=3,
            key=MetadataFieldKey.FLIGHT_ROLL_DEGREE,
        ),
        MetadataFieldKey.FLIGHT_YAW_DEGREE: Field(
            normalized="xmp_bloco_1:drone-dji:FlightYawDegree",
            core="xmp_bloco_1",
            label="Flight Yaw Degree",
            attribute="DroneYaw",
            description="Angulo de yaw da aeronave em graus. [DroneYaw]",
            level=3,
            key=MetadataFieldKey.FLIGHT_YAW_DEGREE,
        ),
        MetadataFieldKey.FLIGHT_PITCH_DEGREE: Field(
            normalized="xmp_bloco_1:drone-dji:FlightPitchDegree",
            core="xmp_bloco_1",
            label="Flight Pitch Degree",
            attribute="DronePitc",
            description="Angulo de pitch da aeronave em graus. [DronePitc]",
            level=3,
            key=MetadataFieldKey.FLIGHT_PITCH_DEGREE,
        ),
        MetadataFieldKey.FLIGHT_X_SPEED: Field(
            normalized="xmp_bloco_1:drone-dji:FlightXSpeed",
            core="xmp_bloco_1",
            label="Flight X Speed",
            attribute="XSpeed",
            description="Velocidade da aeronave no eixo X. [XSpeed]",
            level=3,
            key=MetadataFieldKey.FLIGHT_X_SPEED,
        ),
        MetadataFieldKey.FLIGHT_Y_SPEED: Field(
            normalized="xmp_bloco_1:drone-dji:FlightYSpeed",
            core="xmp_bloco_1",
            label="Flight Y Speed",
            attribute="YSpeed",
            description="Velocidade da aeronave no eixo Y. [YSpeed]",
            level=3,
            key=MetadataFieldKey.FLIGHT_Y_SPEED,
        ),
        MetadataFieldKey.FLIGHT_Z_SPEED: Field(
            normalized="xmp_bloco_1:drone-dji:FlightZSpeed",
            core="xmp_bloco_1",
            label="Flight Z Speed",
            attribute="ZSpeed",
            description="Velocidade da aeronave no eixo Z. [ZSpeed]",
            level=3,
            key=MetadataFieldKey.FLIGHT_Z_SPEED,
        ),
        MetadataFieldKey.RTK_FLAG: Field(
            normalized="xmp_bloco_1:drone-dji:RtkFlag",
            core="xmp_bloco_1",
            label="RTK Flag",
            attribute="RtkFlag",
            description="Indicador de qualidade/correcao RTK. Valores: 0 (sem GPS), 16 (Single), 34 (Float), 50 (Fixed). [RtkFlag]",
            level=3,
            key=MetadataFieldKey.RTK_FLAG,
        ),
        MetadataFieldKey.RTK_STD_LON: Field(
            normalized="xmp_bloco_1:drone-dji:RtkStdLon",
            core="xmp_bloco_1",
            label="RTK Std Lon",
            attribute="RtkStdLon",
            description="Desvio padrao RTK na longitude. [RtkStdLon]",
            level=3,
            key=MetadataFieldKey.RTK_STD_LON,
        ),
        MetadataFieldKey.RTK_STD_LAT: Field(
            normalized="xmp_bloco_1:drone-dji:RtkStdLat",
            core="xmp_bloco_1",
            label="RTK Std Lat",
            attribute="RtkStdLat",
            description="Desvio padrao RTK na latitude. [RtkStdLat]",
            level=3,
            key=MetadataFieldKey.RTK_STD_LAT,
        ),
        MetadataFieldKey.RTK_STD_HGT: Field(
            normalized="xmp_bloco_1:drone-dji:RtkStdHgt",
            core="xmp_bloco_1",
            label="RTK Std Hgt",
            attribute="RtkStdHgt",
            description="Desvio padrao RTK na altitude. [RtkStdHgt]",
            level=3,
            key=MetadataFieldKey.RTK_STD_HGT,
        ),
        MetadataFieldKey.RTK_DIFF_AGE: Field(
            normalized="xmp_bloco_1:drone-dji:RtkDiffAge",
            core="xmp_bloco_1",
            label="RTK Diff Age",
            attribute="RtkDifAge",
            description="Tempo desde a ultima correcao RTK. [RtkDifAge]",
            level=3,
            key=MetadataFieldKey.RTK_DIFF_AGE,
        ),
        MetadataFieldKey.DEWARP_FLAG: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpFlag",
            core="xmp_bloco_1",
            label="Dewarp Flag",
            attribute="Dewarp",
            description="Estado da correcao de distorcao (dewarp). [Dewarp]",
            level=3,
            key=MetadataFieldKey.DEWARP_FLAG,
        ),
        MetadataFieldKey.DEWARP_DATE: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpDate",
            core="xmp_bloco_1",
            label="Dewarp Date",
            attribute="D_Date",
            description="Data do calibrador dewarp extraida do DewarpData. [D_Date]",
            level=3,
            key=MetadataFieldKey.DEWARP_DATE,
        ),
        MetadataFieldKey.DEWARP_FOCAL_X: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpFocalX",
            core="xmp_bloco_1",
            label="Dewarp Focal X",
            attribute="D_FocalX",
            description="Distancia focal X do dewarp em pixels. [D_FocalX]",
            level=3,
            key=MetadataFieldKey.DEWARP_FOCAL_X,
        ),
        MetadataFieldKey.DEWARP_FOCAL_Y: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpFocalY",
            core="xmp_bloco_1",
            label="Dewarp Focal Y",
            attribute="D_FocalY",
            description="Distancia focal Y do dewarp em pixels. [D_FocalY]",
            level=3,
            key=MetadataFieldKey.DEWARP_FOCAL_Y,
        ),
        MetadataFieldKey.DEWARP_CX: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpCx",
            core="xmp_bloco_1",
            label="Dewarp CX",
            attribute="D_CX",
            description="Ponto principal X (center X) do dewarp em pixels. [D_CX]",
            level=3,
            key=MetadataFieldKey.DEWARP_CX,
        ),
        MetadataFieldKey.DEWARP_CY: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpCy",
            core="xmp_bloco_1",
            label="Dewarp CY",
            attribute="D_CY",
            description="Ponto principal Y (center Y) do dewarp em pixels. [D_CY]",
            level=3,
            key=MetadataFieldKey.DEWARP_CY,
        ),
        MetadataFieldKey.DEWARP_K1: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpK1",
            core="xmp_bloco_1",
            label="Dewarp K1",
            attribute="D_K1",
            description="Coeficiente de distorcao radial K1 do dewarp. [D_K1]",
            level=3,
            key=MetadataFieldKey.DEWARP_K1,
        ),
        MetadataFieldKey.DEWARP_K2: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpK2",
            core="xmp_bloco_1",
            label="Dewarp K2",
            attribute="D_K2",
            description="Coeficiente de distorcao radial K2 do dewarp. [D_K2]",
            level=3,
            key=MetadataFieldKey.DEWARP_K2,
        ),
        MetadataFieldKey.DEWARP_K3: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpK3",
            core="xmp_bloco_1",
            label="Dewarp K3",
            attribute="D_K3",
            description="Coeficiente de distorcao radial K3 do dewarp. [D_K3]",
            level=3,
            key=MetadataFieldKey.DEWARP_K3,
        ),
        MetadataFieldKey.DEWARP_P1: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpP1",
            core="xmp_bloco_1",
            label="Dewarp P1",
            attribute="D_P1",
            description="Coeficiente de distorcao tangencial P1 do dewarp. [D_P1]",
            level=3,
            key=MetadataFieldKey.DEWARP_P1,
        ),
        MetadataFieldKey.DEWARP_P2: Field(
            normalized="xmp_bloco_1:drone-dji:DewarpP2",
            core="xmp_bloco_1",
            label="Dewarp P2",
            attribute="D_P2",
            description="Coeficiente de distorcao tangencial P2 do dewarp. [D_P2]",
            level=3,
            key=MetadataFieldKey.DEWARP_P2,
        ),
        MetadataFieldKey.UTC_AT_EXPOSURE: Field(
            normalized="xmp_bloco_1:drone-dji:UTCAtExposure",
            core="xmp_bloco_1",
            label="UTC At Exposure",
            attribute="UTCTime",
            description="Horario UTC exato do momento da exposicao. [UTCTime]",
            level=3,
            key=MetadataFieldKey.UTC_AT_EXPOSURE,
        ),
        MetadataFieldKey.SHUTTER_COUNT: Field(
            normalized="xmp_bloco_1:drone-dji:ShutterCount",
            core="xmp_bloco_1",
            label="Shutter Count",
            attribute="ShotCount",
            description="Total de disparos acumulados da camera. [ShotCount]",
            level=3,
            key=MetadataFieldKey.SHUTTER_COUNT,
        ),
        MetadataFieldKey.FOCUS_DISTANCE: Field(
            normalized="xmp_bloco_1:drone-dji:FocusDistance",
            core="xmp_bloco_1",
            label="Focus Distance",
            attribute="FocusDist",
            description="Distancia de foco usada na captura. [FocusDist]",
            level=3,
            key=MetadataFieldKey.FOCUS_DISTANCE,
        ),
        MetadataFieldKey.CAMERA_SERIAL_NUMBER: Field(
            normalized="xmp_bloco_1:drone-dji:CameraSerialNumber",
            core="xmp_bloco_1",
            label="Camera Serial Number",
            attribute="CameraID",
            description="Numero serial da camera. [CameraID]",
            level=3,
            key=MetadataFieldKey.CAMERA_SERIAL_NUMBER,
        ),
        MetadataFieldKey.DRONE_MODEL: Field(
            normalized="xmp_bloco_1:drone-dji:DroneModel",
            core="xmp_bloco_1",
            label="Drone Model",
            attribute="DronModel",
            description="Modelo da aeronave/drone. [DronModel]",
            level=3,
            key=MetadataFieldKey.DRONE_MODEL,
        ),
        MetadataFieldKey.DRONE_SERIAL_NUMBER: Field(
            normalized="xmp_bloco_1:drone-dji:DroneSerialNumber",
            core="xmp_bloco_1",
            label="Drone Serial Number",
            attribute="DroneID",
            description="Numero serial da aeronave/drone. [DroneID]",
            level=3,
            key=MetadataFieldKey.DRONE_SERIAL_NUMBER,
        ),
        MetadataFieldKey.CAPTURE_UUID: Field(
            normalized="xmp_bloco_1:drone-dji:CaptureUUID",
            core="xmp_bloco_1",
            label="Capture UUID",
            attribute="CaptureID",
            description="Identificador unico do conjunto de captura. [CaptureID]",
            level=3,
            key=MetadataFieldKey.CAPTURE_UUID,
        ),
        MetadataFieldKey.PICTURE_QUALITY: Field(
            normalized="xmp_bloco_1:drone-dji:PictureQuality",
            core="xmp_bloco_1",
            label="Picture Quality",
            attribute="ImgQualit",
            description="Nivel de qualidade/compressao da imagem. [ImgQualit]",
            level=3,
            key=MetadataFieldKey.PICTURE_QUALITY,
        ),
        MetadataFieldKey.SEGMENTOS_TOTAL: Field(
            normalized="JPEG:SegmentosTotal",
            core="xmp_bloco_1",
            label="Segmentos Total",
            attribute="Segments",
            description="Quantidade total de segmentos JPEG lidos. [Segments]",
            level=3,
            key=MetadataFieldKey.SEGMENTOS_TOTAL,
        ),
        MetadataFieldKey.SENSOR_TEMPERATURE: Field(
            normalized="xmp_bloco_1:drone-dji:SensorTemperature",
            core="xmp_bloco_1",
            label="Sensor Temperature",
            attribute="SensTemp",
            description="Temperatura do sensor da camera. [SensTemp]",
            level=3,
            key=MetadataFieldKey.SENSOR_TEMPERATURE,
        ),
        MetadataFieldKey.LRF_STATUS: Field(
            normalized="xmp_bloco_1:drone-dji:LRFStatus",
            core="xmp_bloco_1",
            label="LRF Status",
            attribute="LRFStatus",
            description="Status do laser range finder (LRF). [LRFStatus]",
            level=3,
            key=MetadataFieldKey.LRF_STATUS,
        ),
        MetadataFieldKey.LRF_TARGET_DISTANCE: Field(
            normalized="xmp_bloco_1:drone-dji:LRFTargetDistance",
            core="xmp_bloco_1",
            label="LRF Target Distance",
            attribute="LRFDist",
            description="Distancia medida pelo LRF ate o alvo central. [LRFDist]",
            level=3,
            key=MetadataFieldKey.LRF_TARGET_DISTANCE,
        ),
        MetadataFieldKey.LRF_TARGET_LON: Field(
            normalized="xmp_bloco_1:drone-dji:LRFTargetLon",
            core="xmp_bloco_1",
            label="LRF Target Lon",
            attribute="LRFLong",
            description="Longitude do alvo medida pelo LRF. [LRFLong]",
            level=3,
            key=MetadataFieldKey.LRF_TARGET_LON,
        ),
        MetadataFieldKey.LRF_TARGET_LAT: Field(
            normalized="xmp_bloco_1:drone-dji:LRFTargetLat",
            core="xmp_bloco_1",
            label="LRF Target Lat",
            attribute="LRFLati",
            description="Latitude do alvo medida pelo LRF. [LRFLati]",
            level=3,
            key=MetadataFieldKey.LRF_TARGET_LAT,
        ),
        MetadataFieldKey.LRF_TARGET_ALT: Field(
            normalized="xmp_bloco_1:drone-dji:LRFTargetAlt",
            core="xmp_bloco_1",
            label="LRF Target Alt",
            attribute="LRFY",
            description="Altitude relativa do alvo medida pelo LRF. [LRFY]",
            level=3,
            key=MetadataFieldKey.LRF_TARGET_ALT,
        ),
        MetadataFieldKey.LRF_TARGET_ABS_ALT: Field(
            normalized="xmp_bloco_1:drone-dji:LRFTargetAbsAlt",
            core="xmp_bloco_1",
            label="LRF Target Abs Alt",
            attribute="LrfAbsAlt",
            description="Altitude absoluta do alvo medida pelo LRF. [LrfAbsAlt]",
            level=3,
            key=MetadataFieldKey.LRF_TARGET_ABS_ALT,
        ),
        MetadataFieldKey.WHITE_BALANCE_CCT: Field(
            normalized="xmp_bloco_1:drone-dji:WhiteBalanceCCT",
            core="xmp_bloco_1",
            label="White Balance CCT",
            attribute="WhiteBlc",
            description="Temperatura de cor (Kelvin) no balanco de branco. [WhiteBlc]",
            level=3,
            key=MetadataFieldKey.WHITE_BALANCE_CCT,
        ),
        MetadataFieldKey.SENSOR_FPS: Field(
            normalized="xmp_bloco_1:drone-dji:SensorFPS",
            core="xmp_bloco_1",
            label="Sensor FPS",
            attribute="SensorFPS",
            description="Taxa de amostragem do sensor em FPS. [SensorFPS]",
            level=3,
            key=MetadataFieldKey.SENSOR_FPS,
        ),
        MetadataFieldKey.RECOMMENDED_EXPOSURE_INDEX: Field(
            normalized="EXIF:RecommendedExposureIndex",
            core="xmp_bloco_1",
            label="Recommended Exposure Index",
            attribute="REI",
            description="Indice de exposicao recomendado (REI). [REI]",
            level=3,
            key=MetadataFieldKey.RECOMMENDED_EXPOSURE_INDEX,
        ),
        MetadataFieldKey.LENS_POSITION: Field(
            normalized="xmp_bloco_1:drone-dji:LensPosition",
            core="xmp_bloco_1",
            label="Lens Position",
            attribute="LensPosit",
            description="Posicao da lente no momento da captura. [LensPosit]",
            level=3,
            key=MetadataFieldKey.LENS_POSITION,
        ),
        MetadataFieldKey.LENS_TEMPERATURE: Field(
            normalized="xmp_bloco_1:drone-dji:LensTemperature",
            core="xmp_bloco_1",
            label="Lens Temperature",
            attribute="LensTemp",
            description="Temperatura da lente no momento da captura. [LensTemp]",
            level=3,
            key=MetadataFieldKey.LENS_TEMPERATURE,
        ),
    }

    REQUIRED_FIELDS = {**EXIF_FIELDS, **DJI_XMP_FIELDS}

    INITIAL_FIELDS = {
        MetadataFieldKey.FILE: Field(
            normalized="File",
            core="initial",
            label="File",
            attribute="File",
            description="Nome do arquivo de imagem. [File]",
            level=3,
            key=MetadataFieldKey.FILE,
        ),
        MetadataFieldKey.PATH: Field(
            normalized="Path",
            core="initial",
            label="Path",
            attribute="Path",
            description="Caminho completo do arquivo de imagem. [Path]",
            level=3,
            key=MetadataFieldKey.PATH,
        ),
        MetadataFieldKey.FOLDER_LEVEL_1: Field(
            normalized="FolderLevel1",
            core="initial",
            label="Folder Level 1",
            attribute="FolderL1",
            description="Primeiro nivel de pasta do voo. [FolderL1]",
            level=3,
            key=MetadataFieldKey.FOLDER_LEVEL_1,
        ),
        MetadataFieldKey.FOLDER_LEVEL_2: Field(
            normalized="FolderLevel2",
            core="initial",
            label="Folder Level 2",
            attribute="FolderL2",
            description="Segundo nivel de pasta do voo. [FolderL2]",
            level=3,
            key=MetadataFieldKey.FOLDER_LEVEL_2,
        ),
        MetadataFieldKey.FOLDER_LEVEL_3: Field(
            normalized="FolderLevel3",
            core="initial",
            label="Folder Level 3",
            attribute="FolderL3",
            description="Terceiro nivel de pasta do voo. [FolderL3]",
            level=3,
            key=MetadataFieldKey.FOLDER_LEVEL_3,
        ),
        MetadataFieldKey.FOLDER_LEVEL_4: Field(
            normalized="FolderLevel4",
            core="initial",
            label="Folder Level 4",
            attribute="FolderL4",
            description="Quarto nivel de pasta do voo. [FolderL4]",
            level=3,
            key=MetadataFieldKey.FOLDER_LEVEL_4,
        ),
        MetadataFieldKey.FOLDER_LEVEL_5: Field(
            normalized="FolderLevel5",
            core="initial",
            label="Folder Level 5",
            attribute="FolderL5",
            description="Quinto nivel de pasta do voo. [FolderL5]",
            level=3,
            key=MetadataFieldKey.FOLDER_LEVEL_5,
        ),
        MetadataFieldKey.FLIGHT_NUMBER: Field(
            normalized="FlightNumber",
            core="initial",
            label="Flight Number",
            attribute="FlyNum",
            description="Numero do voo derivado do MRK. [FlyNum]",
            level=3,
            key=MetadataFieldKey.FLIGHT_NUMBER,
        ),
        MetadataFieldKey.FLIGHT_NAME: Field(
            normalized="FlightName",
            core="initial",
            label="Flight Name",
            attribute="FlyNam",
            description="Nome do voo derivado do MRK. [FlyNam]",
            level=3,
            key=MetadataFieldKey.FLIGHT_NAME,
        ),
    }

    CUSTOM_FIELDS = {
        MetadataFieldKey.FILE_TYPE: Field(
            normalized="Custom:FileType",
            core="custom",
            label="File Type",
            attribute="FileType",
            description="Tipo/Extensao do arquivo de imagem (ex.: .JPG). [FileType]",
            level=5,
            key=MetadataFieldKey.FILE_TYPE,
        ),
        MetadataFieldKey.DT_FULL: Field(
            normalized="Custom:DtFull",
            core="custom",
            label="Date Time Full",
            attribute="DateTmFul",
            description="Data/hora compacta no formato YYYYMMDDHHMM. [DateTmFul]",
            level=5,
            key=MetadataFieldKey.DT_FULL,
        ),
        MetadataFieldKey.X_DIFFERENCE: Field(
            normalized="Custom:XDifference",
            core="custom",
            label="Diferença Leste-Oeste (X)",
            attribute="XDiff",
            description="Diferença entre a longitude (Easting/X) do MRK e do metadado das imagens. Representa o desvio na coordenada Leste-Oeste. [XDiff]",
            level=5,
            key=MetadataFieldKey.X_DIFFERENCE,
        ),
        MetadataFieldKey.Y_DIFFERENCE: Field(
            normalized="Custom:YDifference",
            core="custom",
            label="Diferença Norte-Sul (Y)",
            attribute="YDiff",
            description="Diferença entre a latitude (Northing/Y) do MRK e do metadado das imagens. Representa o desvio na coordenada Norte-Sul. [YDiff]",
            level=5,
            key=MetadataFieldKey.Y_DIFFERENCE,
        ),
        MetadataFieldKey.Z_DIFFERENCE: Field(
            normalized="Custom:ZDifference",
            core="custom",
            label="Diferença de Altitude (Z)",
            attribute="ZDiff",
            description="Diferença entre a altitude (cota Z) do MRK e a altitude absoluta do metadado das imagens. Representa o desvio vertical entre as duas fontes. [ZDiff]",
            level=5,
            key=MetadataFieldKey.Z_DIFFERENCE,
        ),
        MetadataFieldKey.XY_DIFFERENCE: Field(
            normalized="Custom:XYDifference",
            core="custom",
            label="Diferença Planimétrica (XY)",
            attribute="XYDiff",
            description="Diferença planimétrica total (2D) entre a posição do MRK e a posição do metadado das imagens, combinando os desvios de Latitude (Norte-Sul) e Longitude (Leste-Oeste). [XYDiff]",
            level=5,
            key=MetadataFieldKey.XY_DIFFERENCE,
        ),
        MetadataFieldKey.THREE_D_DIFFERENCE: Field(
            normalized="Custom:3DDifference",
            core="custom",
            label="Diferença Tridimensional (3D)",
            attribute="3DDiff",
            description="Diferença tridimensional total (3D) entre a posição do MRK e a posição do metadado das imagens, combinando os desvios de Longitude (Leste-Oeste), Latitude (Norte-Sul) e Altitude (Z). [3DDiff]",
            level=5,
            key=MetadataFieldKey.THREE_D_DIFFERENCE,
        ),
        MetadataFieldKey.DT_DATE: Field(
            normalized="Custom:DtDate",
            core="custom",
            label="Date Only",
            attribute="DateOnly",
            description="Data compacta no formato YYYYMMDD. [DateOnly]",
            level=5,
            key=MetadataFieldKey.DT_DATE,
        ),
        MetadataFieldKey.DT_TIME: Field(
            normalized="Custom:DtTime",
            core="custom",
            label="Time Only",
            attribute="TimeOnly",
            description="Horario compacto no formato HHMM. [TimeOnly]",
            level=5,
            key=MetadataFieldKey.DT_TIME,
        ),
        MetadataFieldKey.GIMBAL_OFFSET: Field(
            normalized="xmp_bloco_1:drone-dji:GimbalOffset",
            core="custom",
            label="Gimbal Offset",
            attribute="GimOffset",
            description="Deslocamento angular mínimo do gimbal em relação à aeronave em graus (GimbalYawDegree - FlightYawDegree - 180, normalizado para menor ângulo). Valores: 0-180°. Valor referência: <1°. [GimOffset]",
            level=5,
            key=MetadataFieldKey.GIMBAL_OFFSET,
        ),
        MetadataFieldKey.THREE_D_SPEED: Field(
            normalized="Custom:3DSpeed",
            core="custom",
            label="3 D Speed",
            attribute="3DSpeed",
            description="Velocidade total 3D da aeronave em m/s, calculada como |FlightXSpeed| + |FlightYSpeed| + |FlightZSpeed| (norma L1 com valores absolutos para garantir que velocidades negativas também somem). Valores: 0-50 m/s. Valor referência: <10 m/s para voos estáveis. [3DSpeed]",
            level=5,
            key=MetadataFieldKey.THREE_D_SPEED,
        ),
        MetadataFieldKey.TIME_SINCE_PREVIOUS: Field(
            normalized="Custom:TimeSincePrevious",
            core="custom",
            label="Time Since Previous",
            attribute="TimePrv",
            description="Tempo em segundos desde a foto anterior. Valores: 0-120 s. Valor referência: 2-5 s para cadência ideal. [TimePrv]",
            level=5,
            key=MetadataFieldKey.TIME_SINCE_PREVIOUS,
        ),
        MetadataFieldKey.GEODESIC_DISTANCE_PREVIOUS: Field(
            normalized="Custom:GeodesicDistancePrevious",
            core="custom",
            label="Geodesic Distance Previous",
            attribute="GeoDstP",
            description="Distância horizontal em metros entre posições GPS consecutivas (fórmula Haversine). Valores: 0-100 m. Valor referência: 20-50 m para sobreposição adequada. [GeoDstP]",
            level=5,
            key=MetadataFieldKey.GEODESIC_DISTANCE_PREVIOUS,
        ),
        MetadataFieldKey.DISTANCE_3D_PREVIOUS: Field(
            normalized="Custom:Distance3dPrevious",
            core="custom",
            label="Distance 3 D Previous",
            attribute="Dist3DP",
            description="Distância 3D em metros entre posições consecutivas (horizontal + altitude). Valores: 0-100 m. Valor referência: 20-50 m. [Dist3DP]",
            level=5,
            key=MetadataFieldKey.DISTANCE_3D_PREVIOUS,
        ),
        MetadataFieldKey.AVG_VELOCITY_BETWEEN_PHOTOS: Field(
            normalized="Custom:AvgVelocityBetweenPhotos",
            core="custom",
            label="Avg Velocity Between Photos",
            attribute="AvgVelB",
            description="Velocidade média em m/s entre fotos consecutivas. Valores: 0-20 m/s. Valor referência: 5-10 m/s. [AvgVelB]",
            level=5,
            key=MetadataFieldKey.AVG_VELOCITY_BETWEEN_PHOTOS,
        ),
        MetadataFieldKey.LINEAR_VELOCITY_INSTANT: Field(
            normalized="Custom:LinearVelocityInstant",
            core="custom",
            label="Linear Velocity Instant",
            attribute="LinVelI",
            description="Velocidade instantânea 3D em m/s, calculada como |FlightXSpeed| + |FlightYSpeed| + |FlightZSpeed| (norma L1 com valores absolutos). Valores: 0-50 m/s. Valor referência: <10 m/s. [LinVelI]",
            level=5,
            key=MetadataFieldKey.LINEAR_VELOCITY_INSTANT,
        ),
        MetadataFieldKey.DISPLACEMENT_DIRECTION: Field(
            normalized="Custom:DisplacementDirection",
            core="custom",
            label="Displacement Direction",
            attribute="DirDispl",
            description="Azimute do deslocamento em graus (0=Norte). Valores: 0-360°. Valor referência: varia por missão. [DirDispl]",
            level=5,
            key=MetadataFieldKey.DISPLACEMENT_DIRECTION,
        ),
        MetadataFieldKey.INCIDENCE_ANGLE: Field(
            normalized="Custom:IncidenceAngle",
            core="custom",
            label="Incidence Angle",
            attribute="IncAngle",
            description="Ângulo de incidência em graus (ângulo entre câmera e vertical). Valores: 0-180°. Valor referência: <5° para nadir. [IncAngle]",
            level=5,
            key=MetadataFieldKey.INCIDENCE_ANGLE,
        ),
        MetadataFieldKey.ESTIMATED_COVERAGE: Field(
            normalized="Custom:EstimatedCoverage",
            core="custom",
            label="Estimated Coverage",
            attribute="EstCover",
            description="Tupla (largura, altura) em metros da cobertura estimada no solo. Valores: (0-200, 0-150) m. Valor referência: depende altitude. [EstCover]",
            level=5,
            key=MetadataFieldKey.ESTIMATED_COVERAGE,
        ),
        MetadataFieldKey.COVERAGE_WIDTH: Field(
            normalized="Custom:CoverageWidth",
            core="custom",
            label="Coverage Width",
            attribute="CoverW",
            description="Largura da cobertura estimada no solo em metros. Valores: 0-200 m. [CoverW]",
            level=5,
            key=MetadataFieldKey.COVERAGE_WIDTH,
        ),
        MetadataFieldKey.COVERAGE_HEIGHT: Field(
            normalized="Custom:CoverageHeight",
            core="custom",
            label="Coverage Height",
            attribute="CoverH",
            description="Altura da cobertura estimada no solo em metros. Valores: 0-150 m. [CoverH]",
            level=5,
            key=MetadataFieldKey.COVERAGE_HEIGHT,
        ),
        MetadataFieldKey.PREDICTED_OVERLAP: Field(
            normalized="Custom:PredictedOverlap",
            core="custom",
            label="Predicted Overlap",
            attribute="PredOver",
            description="Percentual de sobreposição longitudinal com foto anterior. Valores: 0-100%. Valor referência: >60%. [PredOver]",
            level=5,
            key=MetadataFieldKey.PREDICTED_OVERLAP,
        ),
        MetadataFieldKey.F_OVERLAP: Field(
            normalized="Custom:FOverlap",
            core="custom",
            label="Frontal Overlap",
            attribute="FOverlap",
            description="Sobreposição frontal (mesmo PredictedOverlap) em percentual. Valores: 0-100%. Valor referência: >60%. [FOverlap]",
            level=5,
            key=MetadataFieldKey.F_OVERLAP,
        ),
        MetadataFieldKey.RTK_EFFECTIVE_PRECISION: Field(
            normalized="Custom:RtkEffectivePrecision",
            core="custom",
            label="RTK Effective Precision",
            attribute="RTKPrec",
            description="Classificação textual da precisão RTK. Valores: Alta, Média, Baixa, Sem RTK. Valor referência: Alta. [RTKPrec]",
            level=5,
            key=MetadataFieldKey.RTK_EFFECTIVE_PRECISION,
        ),
        MetadataFieldKey.RTK_TYPE: Field(
            normalized="Custom:RtkType",
            core="custom",
            label="RTK Type",
            attribute="RtkType",
            description="Classificação do tipo de sinal RTK baseada no RtkFlag. Valores: RTK Fixed (50), RTK Float (34), RTK Single (16), Sem GPS (0). [RtkType]",
            level=5,
            key=MetadataFieldKey.RTK_TYPE,
        ),
        MetadataFieldKey.IS_IDEAL_OVERLAP: Field(
            normalized="Custom:IsIdealOverlap",
            core="custom",
            label="Is Ideal Overlap",
            attribute="IdealOvl",
            description="Booleano indicando se sobreposição >=60%. Valores: True/False. Valor referência: True. [IdealOvl]",
            level=5,
            key=MetadataFieldKey.IS_IDEAL_OVERLAP,
        ),
        MetadataFieldKey.ABRUPT_CHANGE_FLAG: Field(
            normalized="Custom:AbruptChangeFlag",
            core="custom",
            label="Abrupt Change Flag",
            attribute="AbrChgF",
            description="Flag de mudança brusca (tempo ou distância >2x mediana). Valores: True/False. Valor referência: False. [AbrChgF]",
            level=5,
            key=MetadataFieldKey.ABRUPT_CHANGE_FLAG,
        ),
        MetadataFieldKey.GIMBAL_ANGULAR_VELOCITY: Field(
            normalized="Custom:GimbalAngularVelocity",
            core="custom",
            label="Gimbal Angular Velocity",
            attribute="GimAngV",
            description="Variação angular do gimbal em °/s. Valores: 0-100 °/s. Valor referência: <1 °/s. [GimAngV]",
            level=5,
            key=MetadataFieldKey.GIMBAL_ANGULAR_VELOCITY,
        ),
        MetadataFieldKey.ORTHORECTIFICATION_POTENTIAL: Field(
            normalized="Custom:OrthorectificationPotential",
            core="custom",
            label="Orthorectification Potential",
            attribute="OrtoPot",
            description="Score de potencial para ortorretificação (0-100). Valores: 0-100. Valor referência: >80. [OrtoPot]",
            level=5,
            key=MetadataFieldKey.ORTHORECTIFICATION_POTENTIAL,
        ),
        MetadataFieldKey.SHUTTER_LIFE_PCT: Field(
            normalized="Custom:ShutterLifePct",
            core="custom",
            label="Shutter Life Pct",
            attribute="ShutPct",
            description="% de vida útil do obturador. Valores: 0-100%. Valor referência: <50%. [ShutPct]",
            level=5,
            key=MetadataFieldKey.SHUTTER_LIFE_PCT,
        ),
        MetadataFieldKey.GROUND_SAMPLE_DISTANCE_CM: Field(
            normalized="Custom:GroundSampleDistanceCm",
            core="custom",
            label="Ground Sample Distance Cm",
            attribute="GsdCmPx",
            description="GSD em cm/pixel. Valores: 0-10 cm. Valor referência: <2 cm. [GsdCmPx]",
            level=5,
            key=MetadataFieldKey.GROUND_SAMPLE_DISTANCE_CM,
        ),
        MetadataFieldKey.TOTAL_HEAT_INDEX: Field(
            normalized="Custom:TotalHeatIndex",
            core="custom",
            label="Total Heat Index",
            attribute="HeatIdx",
            description="Índice térmico médio em °C. Valores: 20-60 °C. Valor referência: <40 °C. [HeatIdx]",
            level=5,
            key=MetadataFieldKey.TOTAL_HEAT_INDEX,
        ),
        MetadataFieldKey.SPEED_3D_KMH: Field(
            normalized="Custom:Speed3dKmh",
            core="custom",
            label="Speed 3 D Kmh",
            attribute="SpdKmH",
            description="Velocidade 3D do drone em km/h. Valores: 0-180 km/h. Valor referência: <36 km/h. [SpdKmH]",
            level=5,
            key=MetadataFieldKey.SPEED_3D_KMH,
        ),
        MetadataFieldKey.YAW_ALIGNMENT_ERROR: Field(
            normalized="Custom:YawAlignmentError",
            core="custom",
            label="Yaw Alignment Error",
            attribute="YawErr",
            description="Erro de alinhamento yaw em graus. Valores: 0-180°. Valor referência: <5°. [YawErr]",
            level=5,
            key=MetadataFieldKey.YAW_ALIGNMENT_ERROR,
        ),
        MetadataFieldKey.MOTION_BLUR_RISK: Field(
            normalized="Custom:MotionBlurRisk",
            core="custom",
            label="Motion Blur Risk",
            attribute="BlurRisk",
            description="Risco de motion blur em pixels. Valores: 0-5. Valor referência: <0.5. [BlurRisk]",
            level=5,
            key=MetadataFieldKey.MOTION_BLUR_RISK,
        ),
        MetadataFieldKey.EXPOSURE_VALUE_EV: Field(
            normalized="Custom:ExposureValueEv",
            core="custom",
            label="Exposure Value EV",
            attribute="EV",
            description="Valor de exposição EV. Valores: 8-16. Valor referência: 12-14. [EV]",
            level=5,
            key=MetadataFieldKey.EXPOSURE_VALUE_EV,
        ),
        MetadataFieldKey.LIGHT_SOURCE_CLASSIFICATION: Field(
            normalized="Custom:LightSourceClassification",
            core="custom",
            label="Light Source Classification",
            attribute="LSrcClass",
            description="Classificação textual da fonte de luz EXIF. Valores: Daylight, Fluorescent, etc. Valor referência: Daylight. [LSrcClass]",
            level=5,
            key=MetadataFieldKey.LIGHT_SOURCE_CLASSIFICATION,
        ),
        MetadataFieldKey.LIGHT_CONSISTENCY: Field(
            normalized="Custom:LightConsistency",
            core="custom",
            label="Light Consistency",
            attribute="LightCons",
            description="Classificação textual da fonte de luz EXIF (mesmo valor de LightSourceClassification). Valores: Daylight, Fluorescent, etc. Valor referência: Daylight. [LightCons]",
            level=5,
            key=MetadataFieldKey.LIGHT_CONSISTENCY,
        ),
        MetadataFieldKey.VERTICAL_STABILITY: Field(
            normalized="Custom:VerticalStability",
            core="custom",
            label="Vertical Stability",
            attribute="VertStb",
            description="Variação vertical em metros. Valores: 0-10 m. Valor referência: <1 m. [VertStb]",
            level=5,
            key=MetadataFieldKey.VERTICAL_STABILITY,
        ),
        MetadataFieldKey.TRAJECTORY_SMOOTHNESS: Field(
            normalized="Custom:TrajectorySmoothness",
            core="custom",
            label="Trajectory Smoothness",
            attribute="TrajSmt",
            description="Diferença angular de direção em graus. Valores: 0-180°. Valor referência: <10°. [TrajSmt]",
            level=5,
            key=MetadataFieldKey.TRAJECTORY_SMOOTHNESS,
        ),
        MetadataFieldKey.SPEED_VARIATION_INDEX: Field(
            normalized="Custom:SpeedVariationIndex",
            core="custom",
            label="Speed Variation Index",
            attribute="SpdVar",
            description="Índice de variação de velocidade (coeficiente de variação). Valores: 0-1. Valor referência: <0.1. [SpdVar]",
            level=5,
            key=MetadataFieldKey.SPEED_VARIATION_INDEX,
        ),
        MetadataFieldKey.RTK_STABILITY_SCORE: Field(
            normalized="Custom:RtkStabilityScore",
            core="custom",
            label="RTK Stability Score",
            attribute="RtkStab",
            description="Score de estabilidade RTK (0-100). Valores: 0-100. Valor referência: >90. [RtkStab]",
            level=5,
            key=MetadataFieldKey.RTK_STABILITY_SCORE,
        ),
        MetadataFieldKey.CAPTURE_EFFICIENCY: Field(
            normalized="Custom:CaptureEfficiency",
            core="custom",
            label="Capture Efficiency",
            attribute="CapEff",
            description="Eficiência de captura (distância/cobertura). Valores: 0-1. Valor referência: 0.5-0.8. [CapEff]",
            level=5,
            key=MetadataFieldKey.CAPTURE_EFFICIENCY,
        ),
        MetadataFieldKey.PHOTOGRAMMETRY_QUALITY_INDEX: Field(
            normalized="Custom:PhotogrammetryQualityIndex",
            core="custom",
            label="Photogrammetry Quality Index",
            attribute="PQI",
            description="Índice de qualidade fotogramétrica (0-100). Valores: 0-100. Valor referência: >80. [PQI]",
            level=5,
            key=MetadataFieldKey.PHOTOGRAMMETRY_QUALITY_INDEX,
        ),
        MetadataFieldKey.GROUND_ELEVATION: Field(
            normalized="Custom:GroundElevation",
            core="custom",
            label="Ground Elevation",
            attribute="GrndElev",
            description="Altitude do solo (MSL) calculada como AbsoluteAltitude - FlightAltitude. Com LRF: AbsZ - (LRFDist * cos(incidence)). Sem LRF: AbsZ - RelativeAltitude. [GrndElev]",
            level=5,
            key=MetadataFieldKey.GROUND_ELEVATION,
        ),
        MetadataFieldKey.STRIP_ID: Field(
            normalized="Custom:StripId",
            core="custom",
            label="Strip ID",
            attribute="StripID",
            description="ID da faixa de voo. Valores: 1+. Valor referência: incremental. [StripID]",
            level=5,
            key=MetadataFieldKey.STRIP_ID,
        ),
        MetadataFieldKey.EV_CLASSIFICATION: Field(
            normalized="Custom:EvClassification",
            core="custom",
            label="EV Classification",
            attribute="EvClass",
            description="Classificação textual da exposição baseada no EV. Valores: noite/escuro, indoor/sombra, nublado, luz solar normal, sol muito forte/neve. [EvClass]",
            level=5,
            key=MetadataFieldKey.EV_CLASSIFICATION,
        ),
        MetadataFieldKey.FLIGHT_ALTITUDE: Field(
            normalized="Custom:FlightAltitude",
            core="custom",
            label="Flight Altitude",
            attribute="FlyAlt",
            description="Altitude de voo efetiva em metros. Prioridade: LRF_TARGET_DISTANCE corrigido pelo ângulo de incidência > RelativeAltitude. Representa a altura real da câmera em relação ao solo/alvo. [FlyAlt]",
            level=5,
            key=MetadataFieldKey.FLIGHT_ALTITUDE,
        ),
        MetadataFieldKey.FOV: Field(
            normalized="Custom:FOV",
            core="custom",
            label="FOV",
            attribute="FOV",
            description="Field of View (Campo de Visão) — ângulo diagonal total que a câmera enxerga em graus. Fórmula: 2 × arctan(diagonal_sensor / (2 × focal_real)). Valores: 0-180°. Valor referência: ~73-84° para câmeras DJI. [FOV]",
            level=5,
            key=MetadataFieldKey.FOV,
        ),
        MetadataFieldKey.CIRCLE_OF_CONFUSION: Field(
            normalized="Custom:CircleOfConfusion",
            core="custom",
            label="Circle Of Confusion",
            attribute="CoC",
            description="Circle of Confusion — diâmetro máximo de desfoque no sensor ainda percebido como nítido em mm. Fórmula: diagonal_sensor / 1730. Valores: 0-0.05 mm. Valor referência: ~0.015 mm para sensores DJI. [CoC]",
            level=5,
            key=MetadataFieldKey.CIRCLE_OF_CONFUSION,
        ),
        MetadataFieldKey.DOF: Field(
            normalized="Custom:DOF",
            core="custom",
            label="DOF",
            attribute="DOF",
            description="Depth of Field (Profundidade de Campo) em metros — distância total entre o ponto mais próximo e o mais distante do plano focal com nitidez aceitável. Fórmula baseada em FocalLength, FNumber, FocusDistance e CircleOfConfusion. Valores: 0-100 m. Valor referência: ~0.5-50 m. [DOF]",
            level=5,
            key=MetadataFieldKey.DOF,
        ),
        MetadataFieldKey.HYPERFOCAL_DISTANCE: Field(
            normalized="Custom:HyperfocalDistance",
            core="custom",
            label="Hyperfocal Distance",
            attribute="HypDist",
            description="Distância hiperfocal em metros — a menor distância de foco na qual tudo a partir da metade dessa distância até o infinito aparece aceitavelmente nítido. Fórmula: f² / (N × CoC). Valores: 0-100 m. Valor referência: ~3-10 m para câmeras DJI. [HypDist]",
            level=5,
            key=MetadataFieldKey.HYPERFOCAL_DISTANCE,
        ),
        MetadataFieldKey.LIGHT_VALUE: Field(
            normalized="Custom:LightValue",
            core="custom",
            label="Light Value",
            attribute="LightVal",
            description="Light Value (LV / EV100) — medida padronizada da luminosidade da cena no momento da captura. Fórmula: log₂(N² × 100 / (t × ISO)). Valores: 0-20. Valor referência: 12-13 (dia ensolarado), 10-11 (nublado), 8-9 (sombra). [LightVal]",
            level=5,
            key=MetadataFieldKey.LIGHT_VALUE,
        ),
        MetadataFieldKey.FOCAL_LENGTH_35EFL: Field(
            normalized="Custom:FocalLength35efl",
            core="custom",
            label="Focal Length 35 EFL",
            attribute="Focal35",
            description="Distância focal equivalente em 35mm (full frame) — converte a distância focal real para o equivalente full frame usando o fator de corte (crop factor) do sensor. Fórmula: FocalLength × (43.2666 / diagonal_sensor). Valores: 0-1000 mm. Valor referência: ~24 mm para câmeras DJI. [Focal35]",
            level=5,
            key=MetadataFieldKey.FOCAL_LENGTH_35EFL,
        ),
    }

    MRK_FIELDS = {
        MetadataFieldKey.FOTO: Field(
            normalized="MRK:Foto",
            core="mrk",
            label="Photo Number",
            attribute="PhotoNum",
            description="Numero sequencial da foto vindo do MRK. [PhotoNum]",
            level=5,
            key=MetadataFieldKey.FOTO,
        ),
        MetadataFieldKey.LAT: Field(
            normalized="MRK:Lat",
            core="mrk",
            label="Latitude",
            attribute="Latitude",
            description="Latitude extraida do arquivo MRK. [Latitude]",
            level=5,
            key=MetadataFieldKey.LAT,
        ),
        MetadataFieldKey.LON: Field(
            normalized="MRK:Lon",
            core="mrk",
            label="Longitude",
            attribute="Longitude",
            description="Longitude extraida do arquivo MRK. [Longitude]",
            level=5,
            key=MetadataFieldKey.LON,
        ),
        MetadataFieldKey.ALT: Field(
            normalized="MRK:Alt",
            core="mrk",
            label="Altitude",
            attribute="Altitude",
            description="Altitude extraida do arquivo MRK. [Altitude]",
            level=5,
            key=MetadataFieldKey.ALT,
        ),
        MetadataFieldKey.DATE_NAME: Field(
            normalized="MRK:DateName",
            core="mrk",
            label="Date Name",
            attribute="DateName",
            description="Data identificada a partir do nome do MRK. [DateName]",
            level=5,
            key=MetadataFieldKey.DATE_NAME,
        ),
        MetadataFieldKey.MRK_FILE: Field(
            normalized="MRK:MrkFile",
            core="mrk",
            label="MRK File",
            attribute="MrkFile",
            description="Nome do arquivo MRK de origem. [MrkFile]",
            level=5,
            key=MetadataFieldKey.MRK_FILE,
        ),
        MetadataFieldKey.MRK_PATH: Field(
            normalized="MRK:MrkPath",
            core="mrk",
            label="MRK Path",
            attribute="MrkPath",
            description="Caminho completo do arquivo MRK de origem. [MrkPath]",
            level=5,
            key=MetadataFieldKey.MRK_PATH,
        ),
        MetadataFieldKey.MRK_FOLDER: Field(
            normalized="MRK:MrkFolder",
            core="mrk",
            label="MRK Folder",
            attribute="MrkFolder",
            description="Pasta absoluta de origem do ponto MRK. [MrkFolder]",
            level=5,
            key=MetadataFieldKey.MRK_FOLDER,
        ),
        MetadataFieldKey.FLIGHT_NUMBER: Field(
            normalized="MRK:FlightNumber",
            core="mrk",
            label="Flight Number",
            attribute="FlightNum",
            description="Numero do voo identificado no MRK. [FlightNum]",
            level=5,
            key=MetadataFieldKey.FLIGHT_NUMBER,
        ),
        MetadataFieldKey.FLIGHT_NAME: Field(
            normalized="MRK:FlightName",
            core="mrk",
            label="Flight Name",
            attribute="FlightNam",
            description="Nome do voo identificado no MRK. [FlightNam]",
            level=5,
            key=MetadataFieldKey.FLIGHT_NAME,
        ),
        MetadataFieldKey.FOLDER_LEVEL_1: Field(
            normalized="MRK:FolderLevel1",
            core="mrk",
            label="Folder Level 1",
            attribute="Folder1",
            description="Primeiro nivel de pasta no caminho do MRK. [Folder1]",
            level=5,
            key=MetadataFieldKey.FOLDER_LEVEL_1,
        ),
        MetadataFieldKey.FOLDER_LEVEL_2: Field(
            normalized="MRK:FolderLevel2",
            core="mrk",
            label="Folder Level 2",
            attribute="Folder2",
            description="Segundo nivel de pasta no caminho do MRK. [Folder2]",
            level=5,
            key=MetadataFieldKey.FOLDER_LEVEL_2,
        ),
    }

    CAMERA_MODEL_PARAMS = CAMERA_SPECS = {
        # =========================================================
        # DJI ENTERPRISE / MAPPING
        # =========================================================
        "M4E": {
            "name": "DJI Matrice 4 Enterprise",
            "sensor_type": "4/3 CMOS",
            "sensor_width_mm": 17.3,
            "sensor_height_mm": 13.0,
            "resolution_px": (5280, 3956),
            "megapixels": 20,
            "focal_real_mm": 12.29,
            "focal_eq_mm": 24,
            "pixel_size_um": 3.3,
            "mechanical_shutter": True,
        },
        "M3E": {
            "name": "DJI Mavic 3 Enterprise",
            "sensor_type": "4/3 CMOS",
            "sensor_width_mm": 17.3,
            "sensor_height_mm": 13.0,
            "resolution_px": (5280, 3956),
            "megapixels": 20,
            "focal_real_mm": 12.29,
            "focal_eq_mm": 24,
            "pixel_size_um": 3.3,
            "mechanical_shutter": True,
        },
        "M3M": {
            "name": "DJI Mavic 3 Multispectral",
            "sensor_type": "4/3 CMOS RGB + Multispectral",
            "sensor_width_mm": 17.3,
            "sensor_height_mm": 13.0,
            "resolution_px": (5280, 3956),
            "megapixels": 20,
            "focal_real_mm": 12.29,
            "focal_eq_mm": 24,
            "pixel_size_um": 3.3,
            "mechanical_shutter": True,
        },
        "M3T": {
            "name": "DJI Mavic 3 Thermal",
            "sensor_type": "1/2 CMOS",
            "sensor_width_mm": 6.4,
            "sensor_height_mm": 4.8,
            "resolution_px": (4000, 3000),
            "megapixels": 12,
            "focal_real_mm": 6.7,
            "focal_eq_mm": 24,
            "pixel_size_um": 1.6,
            "mechanical_shutter": False,
        },
        "FC6310R": {
            "name": "DJI Phantom 4 RTK",
            "sensor_type": "1-inch CMOS",
            "sensor_width_mm": 13.2,
            "sensor_height_mm": 8.8,
            "resolution_px": (5472, 3648),
            "megapixels": 20,
            "focal_real_mm": 8.8,
            "focal_eq_mm": 24,
            "pixel_size_um": 2.41,
            "mechanical_shutter": True,
        },
        "FC6520": {
            "name": "DJI Phantom 4 Pro V2",
            "sensor_type": "1-inch CMOS",
            "sensor_width_mm": 13.2,
            "sensor_height_mm": 8.8,
            "resolution_px": (5472, 3648),
            "megapixels": 20,
            "focal_real_mm": 8.8,
            "focal_eq_mm": 24,
            "pixel_size_um": 2.41,
            "mechanical_shutter": True,
        },
        "Zenmuse P1": {
            "name": "DJI Zenmuse P1",
            "sensor_type": "Full Frame",
            "sensor_width_mm": 35.9,
            "sensor_height_mm": 24.0,
            "resolution_px": (8192, 5460),
            "megapixels": 45,
            "focal_real_mm": 35.0,
            "focal_eq_mm": 35,
            "pixel_size_um": 4.4,
            "mechanical_shutter": True,
        },
        "L2": {
            "name": "DJI Zenmuse L2",
            "sensor_type": "4/3 CMOS",
            "sensor_width_mm": 17.3,
            "sensor_height_mm": 13.0,
            "resolution_px": (5280, 3956),
            "megapixels": 20,
            "focal_real_mm": 12.29,
            "focal_eq_mm": 24,
            "pixel_size_um": 3.3,
            "mechanical_shutter": True,
            # LiDAR
            "lidar": True,
            "lidar_max_returns": 5,
            "lidar_points_per_second": 1200000,
            "lidar_max_range_m": 450,
            "lidar_fov_horizontal_deg": 70,
            "lidar_fov_vertical_deg": 75,
        },
        "L1D-20c": {
            "name": "DJI Zenmuse L1 RGB",
            "sensor_type": "1-inch CMOS",
            "sensor_width_mm": 13.2,
            "sensor_height_mm": 8.8,
            "resolution_px": (5472, 3648),
            "megapixels": 20,
            "focal_real_mm": 8.8,
            "focal_eq_mm": 24,
            "pixel_size_um": 2.4,
            "mechanical_shutter": True,
        },
        "ZH20T": {
            "name": "DJI Zenmuse H20T Wide",
            "sensor_type": "1/2.3 CMOS",
            "sensor_width_mm": 6.3,
            "sensor_height_mm": 4.7,
            "resolution_px": (4056, 3040),
            "megapixels": 12,
            "focal_real_mm": 4.5,
            "focal_eq_mm": 24,
            "pixel_size_um": 1.55,
            "mechanical_shutter": False,
        },
        # =========================================================
        # DJI CONSUMER
        # =========================================================
        "M3C": {
            "name": "DJI Mavic 3 Classic",
            "sensor_type": "4/3 CMOS",
            "sensor_width_mm": 17.3,
            "sensor_height_mm": 13.0,
            "resolution_px": (5280, 3956),
            "megapixels": 20,
            "focal_real_mm": 12.29,
            "focal_eq_mm": 24,
            "pixel_size_um": 3.3,
            "mechanical_shutter": False,
        },
        "M3P": {
            "name": "DJI Mavic 3 Pro",
            "sensor_type": "4/3 CMOS",
            "sensor_width_mm": 17.3,
            "sensor_height_mm": 13.0,
            "resolution_px": (5280, 3956),
            "megapixels": 20,
            "focal_real_mm": 12.29,
            "focal_eq_mm": 24,
            "pixel_size_um": 3.3,
            "mechanical_shutter": False,
        },
        "AIR3": {
            "name": "DJI Air 3",
            "sensor_type": "1/1.3 CMOS",
            "sensor_width_mm": 9.6,
            "sensor_height_mm": 7.2,
            "resolution_px": (8064, 6048),
            "megapixels": 48,
            "focal_real_mm": 6.7,
            "focal_eq_mm": 24,
            "pixel_size_um": 1.2,
            "mechanical_shutter": False,
        },
        "MINI4PRO": {
            "name": "DJI Mini 4 Pro",
            "sensor_type": "1/1.3 CMOS",
            "sensor_width_mm": 9.6,
            "sensor_height_mm": 7.2,
            "resolution_px": (8064, 6048),
            "megapixels": 48,
            "focal_real_mm": 6.7,
            "focal_eq_mm": 24,
            "pixel_size_um": 1.2,
            "mechanical_shutter": False,
        },
        # =========================================================
        # AUTEL
        # =========================================================
        "EVO2PRO": {
            "name": "Autel EVO II Pro",
            "sensor_type": "1-inch CMOS",
            "sensor_width_mm": 13.2,
            "sensor_height_mm": 8.8,
            "resolution_px": (5472, 3648),
            "megapixels": 20,
            "focal_real_mm": 10.26,
            "focal_eq_mm": 28,
            "pixel_size_um": 2.4,
            "mechanical_shutter": False,
        },
        "EVO_MAX_4T": {
            "name": "Autel EVO Max 4T",
            "sensor_type": "1-inch CMOS",
            "sensor_width_mm": 13.2,
            "sensor_height_mm": 8.8,
            "resolution_px": (5472, 3648),
            "megapixels": 50,
            "focal_real_mm": 10.5,
            "focal_eq_mm": 23,
            "pixel_size_um": 2.4,
            "mechanical_shutter": False,
        },
        # =========================================================
        # PARROT
        # =========================================================
        "ANAFI_AI": {
            "name": "Parrot Anafi AI",
            "sensor_type": "1/1.56 CMOS",
            "sensor_width_mm": 8.2,
            "sensor_height_mm": 6.1,
            "resolution_px": (5344, 4016),
            "megapixels": 48,
            "focal_real_mm": 6.0,
            "focal_eq_mm": 23,
            "pixel_size_um": 1.22,
            "mechanical_shutter": False,
        },
        # =========================================================
        # SKYDIO
        # =========================================================
        "X10": {
            "name": "Skydio X10",
            "sensor_type": "1/1.8 CMOS",
            "sensor_width_mm": 7.2,
            "sensor_height_mm": 5.4,
            "resolution_px": (4096, 3072),
            "megapixels": 12,
            "focal_real_mm": 4.5,
            "focal_eq_mm": 24,
            "pixel_size_um": 1.55,
            "mechanical_shutter": False,
        },
    }

    @classmethod
    def all_fields(cls) -> Dict[str, Field]:
        fields: Dict[str, Field] = {}
        fields.update({key.value: field for key, field in cls.INITIAL_FIELDS.items()})
        fields.update({key.value: field for key, field in cls.EXIF_FIELDS.items()})
        fields.update({key.value: field for key, field in cls.DJI_XMP_FIELDS.items()})
        fields.update({key.value: field for key, field in cls.CUSTOM_FIELDS.items()})
        fields.update({key.value: field for key, field in cls.MRK_FIELDS.items()})
        return fields

    @staticmethod
    def _to_pascal_case(value: str) -> str:
        if not value:
            return value
        parts = [part for part in str(value).split("_") if part]
        if not parts:
            return str(value)
        return "".join(part[:1].upper() + part[1:] for part in parts)

    @classmethod
    def exif_keys(cls) -> List[str]:
        return [key.value for key in cls.EXIF_FIELDS.keys()]

    @classmethod
    def xmp_keys(cls) -> List[str]:
        return [key.value for key in cls.DJI_XMP_FIELDS.keys()]

    @classmethod
    def required_keys(cls) -> List[str]:
        return [key.value for key in cls.EXIF_FIELDS.keys()] + [
            key.value for key in cls.DJI_XMP_FIELDS.keys()
        ]

    @classmethod
    def custom_keys(cls) -> List[str]:
        return [key.value for key in cls.CUSTOM_FIELDS.keys()]

    @classmethod
    def mrk_keys(cls) -> List[str]:
        return [key.value for key in cls.MRK_FIELDS.keys()]

    @classmethod
    def initial_keys(cls) -> List[str]:
        return [key.value for key in cls.INITIAL_FIELDS.keys()]

    @classmethod
    def key_to_attribute_map(cls) -> Dict[str, str]:
        return {key.value: field.attribute for key, field in cls.all_fields().items()}

    @classmethod
    def sanitize_field_name(cls, raw_field_name: str) -> Optional[str]:
        """
        Mapeia nomes de campos brutos/ilegais para campos canonizados em MetadataFields.

        Realiza as seguintes normalizacoes:
        1. Remove espacos e converte para PascalCase
        2. Remove prefixos de namespace (xmp:, drone-dji:, crs:, tiff:, rdf:)
        3. Mapeia campos de sistema (arquivo, caminho, etc.) para canonicos
        4. Valida contra MetadataFields.all_fields()

        Args:
            raw_field_name: Nome bruto do campo (ex: "xmp:CreateDate", "arquivo", "tamanho_mb")

        Returns:
            Nome canonizado do atributo se mapeado com sucesso, None caso contrario
        """
        if not raw_field_name or not isinstance(raw_field_name, str):
            return None

        # Remove espacos
        normalized = raw_field_name.strip()

        # Remove prefixos de namespace
        namespace_prefixes = (
            "xmp:",
            "drone-dji:",
            "crs:",
            "tiff:",
            "rdf:",
            "EXIF:",
            "GPS:",
        )
        for prefix in namespace_prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break

        # Mapeamento especial para campos de sistema e variantes
        field_mappings = {
            "arquivo": "File",
            "caminho": "Path",
            "tamanho_mb": "SizeMb",
            "data_criacao": "DateTime",
            "dt_criacao": "DateTime",
            "os_date": "DateTime",
            "folder_path": "FolderLevel1",
            "voo_id": "FlightNumber",
            "width_px": "ExifImageWidth",
            "height_px": "ExifImageHeight",
            "coverage_width": "EstimatedCoverage",
            # Variantes de nomes EXIF brutos (sem prefixo)
            "gpsstatus": "GpsStatusExif",
            "gpsversionid": "GpsVersionId",
            "gpsaltituderef": "GpsAltRef",
            "gpsaltitude": "GpsAltitude",
            "gpslatituderef": "GpsLatRef",
            "gpslongituderef": "GpsLongRef",
            # Variantes de datas
            "createdate": "DateTime",
            "modifydate": "DateTime",
        }

        # Antes de remover prefixos, verifica se eh campo namespaced XMP especifico
        # Esses precisam mapear para atributos XMP (nao EXIF) para evitar conflitos
        normalized_lower_full = raw_field_name.strip().lower()
        xmp_specific_mappings = {
            "drone-dji:gpsstatus": "GpsStatusXmp",
            "xmp:gpsstatus": "GpsStatusXmp",
            "drone-dji:gpslatitude": "GpsLatXmp",
            "xmp:gpslatitude": "GpsLatXmp",
            "drone-dji:gpslongitude": "GPSLongXmp",
            "xmp:gpslongitude": "GPSLongXmp",
        }
        if normalized_lower_full in xmp_specific_mappings:
            return xmp_specific_mappings[normalized_lower_full]

        # Verifica mapeamento especial (case-insensitive) APOS limpeza de prefixo
        normalized_lower = normalized.lower()
        if normalized_lower in field_mappings:
            return field_mappings[normalized_lower]

        # Tenta encontrar nos campos canonicos
        all_fields_dict = cls.all_fields()

        # Primeiro: busca exata (case-sensitive)
        if normalized in all_fields_dict:
            return all_fields_dict[normalized].attribute

        # Segundo: busca case-insensitive
        normalized_lower = normalized.lower()
        for field_name, field_obj in all_fields_dict.items():
            if field_name.lower() == normalized_lower:
                return field_obj.attribute

        # Terceiro: tenta conversao para PascalCase
        pascal_case = cls._to_pascal_case(
            normalized.replace(" ", "_").replace("-", "_")
        )
        for field_name, field_obj in all_fields_dict.items():
            if field_name.lower() == pascal_case.lower():
                return field_obj.attribute

        # Nenhuma correspondencia encontrada
        return None

    @classmethod
    def is_authorized_field(cls, field_name: str) -> bool:
        """
        Verifica se um nome de campo e um dos campos autorizados em MetadataFields.

        Args:
            field_name: Nome do campo a validar

        Returns:
            True se o campo e autorizado, False caso contrario
        """
        return cls.sanitize_field_name(field_name) is not None

    @classmethod
    def attribute_to_key_map(cls) -> Dict[str, str]:
        return {field.attribute: key for key, field in cls.all_fields().items()}

    @classmethod
    def get_field(cls, key: str) -> Optional[Field]:
        return cls.all_fields().get(cls.resolve_key(key))

    @classmethod
    def get_attribute(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        field = cls.get_field(key)
        if field is None:
            return default
        return field.attribute

    @classmethod
    def resolve_key(cls, key_or_attribute: str) -> str:
        if not key_or_attribute:
            return key_or_attribute

        if key_or_attribute in cls.all_fields():
            return key_or_attribute

        if key_or_attribute in cls.attribute_to_key_map():
            return cls.attribute_to_key_map()[key_or_attribute]

        candidate = cls._to_pascal_case(key_or_attribute)
        if candidate in cls.all_fields():
            return candidate

        return key_or_attribute

    @classmethod
    def resolve_candidates(cls, key_or_attribute: str) -> List[str]:
        """
        Retorna lista ordenada de candidatos de chave canonica para lookup robusto.

        Suporta:
        - chave canonica (ex.: `SizeMb`)
        - attribute (ex.: `SizeMB`)
        - formatos com namespace/prefixo (ex.: `EXIF:SizeMb`, `xmp_bloco_1:drone-dji:GpsLatitude`)
        - variantes normalizadas em snake_case/PascalCase.
        """
        if not key_or_attribute:
            return []

        raw = str(key_or_attribute).strip()
        if not raw:
            return []

        seen = set()
        out: List[str] = []

        def _push(value: str):
            if value and value not in seen:
                seen.add(value)
                out.append(value)

        _push(raw)
        _push(cls.resolve_key(raw))

        # Se vier com namespace (EXIF:, MRK:, xmp_bloco_1:drone-dji:...), tenta sufixos.
        parts = [p for p in raw.split(":") if p]
        if len(parts) > 1:
            tail = parts[-1]
            _push(tail)
            _push(cls.resolve_key(tail))

        # Variantes por estilo de nome (snake -> Pascal etc.)
        pascal = cls._to_pascal_case(raw)
        _push(pascal)
        _push(cls.resolve_key(pascal))

        if len(parts) > 1:
            tail_pascal = cls._to_pascal_case(parts[-1])
            _push(tail_pascal)
            _push(cls.resolve_key(tail_pascal))

        # Mantem apenas candidatos que realmente existem no catalogo.
        catalog = cls.all_fields()
        return [candidate for candidate in out if candidate in catalog]

    @classmethod
    def resolve_output_name(cls, key_or_attribute: str) -> str:
        if not key_or_attribute:
            return key_or_attribute

        resolved_key = cls.resolve_key(key_or_attribute)
        if resolved_key in cls.all_fields():
            return cls.all_fields()[resolved_key].attribute

        if key_or_attribute in cls.attribute_to_key_map():
            return key_or_attribute

        return key_or_attribute

    @classmethod
    def resolve_output_names(cls, names: Iterable[str]) -> List[str]:
        resolved = [cls.resolve_output_name(name) for name in (names or [])]
        return StringAdapter.unique_preserve_order(resolved)

    @classmethod
    def normalize_selected_keys(
        cls,
        names: Iterable[str],
        *,
        allowed_keys: Optional[Iterable[str]] = None,
    ) -> List[str]:
        normalized = [cls.resolve_key(name) for name in (names or [])]
        normalized = StringAdapter.unique_preserve_order(normalized)
        if allowed_keys is None:
            return StringAdapter.filter_known_keys(normalized, cls.all_fields())

        allowed_set = set(allowed_keys)
        return [name for name in normalized if name in allowed_set]

    @classmethod
    def normalize_record_to_keys(cls, record: Dict[str, object]) -> Dict[str, object]:
        """
        Converte um registro com nomes de atributos de camada para chaves internas de metadata.
        Campos nao catalogados sao mantidos inalterados.
        """
        normalized = {}
        for key, value in (record or {}).items():
            candidates = cls.resolve_candidates(key)
            target_key = candidates[0] if candidates else cls.resolve_key(key)

            if target_key not in normalized:
                normalized[target_key] = value
                continue

            current_value = normalized.get(target_key)
            current_empty = current_value in (None, "")
            new_empty = value in (None, "")

            # Nao sobrescrever valor preenchido por valor vazio.
            if current_empty and (not new_empty):
                normalized[target_key] = value
        return normalized

    @classmethod
    def map_record_to_output_attributes(
        cls,
        record: Dict[str, object],
        *,
        exclude_keys: Optional[Iterable[str]] = None,
    ) -> Dict[str, object]:
        """
        Converte um registro baseado em chaves internas para nomes de atributos finais.
        """
        excluded = set(exclude_keys or [])
        mapped = {}
        for key, value in (record or {}).items():
            if key in excluded:
                continue
            mapped[cls.resolve_output_name(key)] = value
        return mapped

    @classmethod
    def default_track_attribute_keys(cls) -> List[str]:
        """
        Chaves canonicas para atributos da camada de trilha.
        """
        return [
            "DateName",
            "FolderLevel1",
            "FolderLevel2",
            "MrkFile",
            "MrkPath",
            "FlightNumber",
            "FlightName",
        ]
