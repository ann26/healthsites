__author__ = 'Irwan Fathurrahman <irwan@kartoza.com>'
__date__ = '22/01/19'

import json
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField
)
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer, GeometrySerializerMethodField, )
from localities_healthsites_osm.models.locality_healthsites_osm import (
    LocalityHealthsitesOSM
)
from localities_osm.models.locality import (
    LocalityOSMView, LocalityOSM
)
from localities.utils import get_locality_detail

attributes_fields = LocalityOSM._meta.get_all_field_names()
attributes_fields.remove('osm_id')


class LocalityHealthsitesOSMBaseSerializer(object):
    def get_attributes(self, obj):
        attributes = {}
        for attribute in attributes_fields:
            attributes[attribute] = getattr(obj, attribute)
        return attributes

    def get_healthsites_data(self, healthsite_osm):
        if healthsite_osm.osm_id and healthsite_osm.osm_type:
            locality_healthsites_osm = LocalityHealthsitesOSM.objects.filter(
                osm_id=healthsite_osm.osm_id,
                osm_type=healthsite_osm.osm_type
            )
            if locality_healthsites_osm.count() == 0:
                return {}
        else:
            locality_healthsites_osm = LocalityHealthsitesOSM.objects.filter(
                osm_pk=healthsite_osm.row.split('-')[0]
            )
            if locality_healthsites_osm.count() == 0:
                return {}
        data = get_locality_detail(locality_healthsites_osm[0].healthsite, None)
        return data


class LocalityHealthsitesOSMSerializer(LocalityHealthsitesOSMBaseSerializer,
                                       ModelSerializer):
    geometry = GeometrySerializerMethodField
    attributes = SerializerMethodField()

    class Meta:
        model = LocalityOSMView
        exclude = []

    def get_geometry(self, obj):
        return obj.geometry.centroid

    def to_representation(self, instance):
        result = super(LocalityHealthsitesOSMSerializer, self).to_representation(instance)
        locality_data = self.get_healthsites_data(instance)
        try:
            locality_data['attributes'] = locality_data['values']
            del locality_data['values']
        except KeyError:
            locality_data['attributes'] = {}
        # get healthsites locality data and put it on result attributes
        attributes = result['attributes']
        result.update(locality_data)
        for key, value in attributes.items():
            if value:
                if key == 'doctors' or key == 'nurses':
                    locality_data['attributes']['staff'] = '%s|%s' % (
                        attributes['doctors'], attributes['nurses'])
                elif key == 'full_time_beds':
                    try:
                        inpatient_services = list(
                            locality_data['attributes']['inpatient_service'])
                        inpatient_services[0] = attributes['full_time_beds']
                        locality_data['attributes']['inpatient_service'] = \
                            ''.join(inpatient_services)
                    except KeyError:
                        locality_data['attributes']['inpatient_service'] = \
                            '%s|' % attributes['full_time_beds']
                else:
                    locality_data['attributes'][key] = value
        locality_data['geometry'] = json.loads(self.get_geometry(instance).geojson)
        locality_data['row'] = result['row']
        locality_data['osm_id'] = result['osm_id']
        locality_data['osm_type'] = result['osm_type']
        return locality_data


class LocalityHealthsitesOSMGeoSerializer(LocalityHealthsitesOSMBaseSerializer,
                                          GeoFeatureModelSerializer):
    attributes = SerializerMethodField()

    class Meta:
        model = LocalityOSMView
        geo_field = 'geometry'
        exclude = attributes_fields
