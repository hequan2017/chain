from django.test import TestCase
from rest_framework.test import APIRequestFactory

from asset.api import AssetList
from asset.models import AssetBusiness, AssetInfo, AssetProject, DockerHost, K8sCluster


class AssetListApiQueryTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = AssetList.as_view()

        self.project_ops = AssetProject.objects.create(projects='ops')
        self.project_dev = AssetProject.objects.create(projects='dev')
        self.business_pay = AssetBusiness.objects.create(business='payment')
        self.business_oa = AssetBusiness.objects.create(business='office')

        AssetInfo.objects.create(
            hostname='ops-web-01',
            network_ip='10.0.0.1',
            inner_ip='8.8.8.8',
            platform='AWS',
            region='东京',
            project=self.project_ops,
            business=self.business_pay,
            is_active=True,
        )
        AssetInfo.objects.create(
            hostname='dev-api-01',
            network_ip='10.0.0.2',
            inner_ip='1.1.1.1',
            platform='AWS',
            region='东京',
            project=self.project_dev,
            business=self.business_oa,
            is_active=False,
        )

    def test_keyword_filter_matches_hostname(self):
        request = self.factory.get('/asset/api/asset.html', {'keyword': 'ops-web'})
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['hostname'], 'ops-web-01')

    def test_is_active_filter_matches_boolean_text(self):
        request = self.factory.get('/asset/api/asset.html', {'is_active': 'false'})
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['hostname'], 'dev-api-01')

    def test_invalid_ordering_falls_back_to_default(self):
        request = self.factory.get('/asset/api/asset.html', {'ordering': 'bad_field'})
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['hostname'], 'dev-api-01')


class ContainerModelTests(TestCase):
    def test_docker_and_k8s_model_str(self):
        project = AssetProject.objects.create(projects='platform')
        business = AssetBusiness.objects.create(business='container')

        docker = DockerHost.objects.create(name='docker-prod', endpoint='tcp://10.0.0.10:2375', project=project, business=business)
        k8s = K8sCluster.objects.create(name='k8s-prod', api_server='https://10.0.0.11:6443', project=project, business=business)

        self.assertEqual(str(docker), 'docker-prod')
        self.assertEqual(str(k8s), 'k8s-prod')
