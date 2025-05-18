<template>
    <div class="copyright">
        ©2025 xiaozhi-esp32-server v{{ version }}
      <div style="margin:0 auto;white-space: nowrap;">
        <a v-if="beianGaNum !== 'null'" :href="'http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=' + beianGaNum" target="_blank" style="text-decoration:none;" rel="noopener">
          <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAMAAABhEH5lAAACXlBMVEUAAADax4rGxqP556zmsVD/6KXu5JvwvFPglEFnY3nnpEjosU1+XFTmuVfu13Hrv1jpsFa1k3mne2HlvnPdqmPqz3fu3YrJoWv04J/mz5z246aSi3i2p2/0zGj82WDrtFjar1O7klO4dkfimUJcWnbho0rgr1vntFfmvFflvGOZdFKXZkOUemnmv2XkuWWVe2ziqlXnt1Tr0HDpwl6ObmCkbEKqhVyOc2jdoVHmuljfrmDq0nPapWDUnErqy3XjtWXesXLrzHjz34rqzYfmw3fy4YrqyYDevW/dzoTIhkndsXLRsIneuHjlyIzQroTjuXjlyYfktWvw2prhvoHTmGfx45j3773TuYT/25LdijyKf321oXU+Nm3cumXfuWLtwlzpwVz40FvpvlvqvFfouFXjrlHipEjcmEfknEXPbzfbZyzZQR/YMBrWKBrhJhLdHxDTGg5HV4xBT4YYKYaWk4SDgYIWIYBybH0qLn1KS3tlZHpNS3WGfHIcHXEwLHAnF28rKW07NGuzn2pNQ2ruzWnDrGnuy2jryGjAnGgoH2j1x2RCNGPcrmIsEGGQdl/pu17YtV7FoV3muVxoRVzWqFvSmVp2SVbyw1XbkVTuvFPfo1PgmVPpt1LcnFLWkVLlp1F7W1HpsU92QE5oMUtFAUrpqUjnjUFOAEHUgz+DUj14FzvbczieMTdhATfodjXWcDXcbjXVcTS/Xi/hay7WXS3cWS3vYyvaVSrUVymnJSjXSyeKDSbNSiWfHCPMTyLFQiHkSR/lPxvVLRrPLBnUJRfUHhbaJxXVGxTZJxPNFhBdOhm/AAAAWXRSTlMABQIU/hIJ/v79/Pj29PPx4cC6s7CNfmxZWRv+/v7+/v7+/v78/Pr6+fPz8vHq6ujl5eTj4ODe2NTQzMW6ubKsnJeQkJCJiIOBgX9ubGpoW1lMREM0JR8dDgvYx1gAAAE7SURBVBjTYgADJmZJQUFJZiYGOGD2EzLV1jIT8paCibCJ86zctGPD1D4ecUaICKuPyYLMYznZOfNqzP0jwEJBOt1KB4/mHjqZ3dGsHwxW5M4Zk5l/PPdIQcGMShUPVqBlgQLlMSvyDq+P3HVidjWnkQQTA5MXV1SFYtb+jZGrl02si2J3Y2JgFMmILl68efueLVvXLSqLXirCCBgDow1HT+GS/AP7srblLS+K5bIHCjmodpXUr929d+eaVb3SsuouQCHhufPjShsbJk/rrK2KW8hiBxRyVkvnkI9tnaDQJDNFOU1DDOjRMEfe9Mjpiewz5RIzZmmKMoPcKqGbkJqSkBSfnDqpXS+ACeRpJ76W/uSUpDlpLPFtfK5soLAKFbU05Odm4eblN7YWk4KEGWOIp62FgYCVsG84SAAAL7BaooX965sAAAAASUVORK5CYII=" style="width:16px;height:16px;vertical-align:middle;">
          <span style="color:#939393;font-size:12px;vertical-align:middle;">{{beianGaNum}}</span>
        </a>
        <span v-if="beianGaNum !== 'null' && beianIcpNum !== 'null'" style="margin:0 5px">
          |
        </span>
        <a v-if="beianIcpNum !== 'null'" href="https://beian.miit.gov.cn/" target="_blank" style="text-decoration:none;" rel="noopener">
          <span style="color:#939393;font-size:12px;vertical-align:middle;">{{beianIcpNum}}</span>
        </a>
      </div>
    </div>
</template>

<script>
import { mapState } from 'vuex';

export default {
    name: 'VersionFooter',
    computed: {
        ...mapState({
          version: state => state.pubConfig.version,
          beianIcpNum: state => state.pubConfig.beianIcpNum,
          beianGaNum: state => state.pubConfig.beianGaNum
        })
    },
    mounted() {
        this.$store.dispatch('fetchPubConfig');
    }
}
</script>

<style scoped>
.footer-record {
  clear: both;
  padding-top: 5px;

}
.footer-icon-record2 {
  width: 100px;
  background-image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAMAAABhEH5lAAACXlBMVEUAAADax4rGxqP556zmsVD/6KXu5JvwvFPglEFnY3nnpEjosU1+XFTmuVfu13Hrv1jpsFa1k3mne2HlvnPdqmPqz3fu3YrJoWv04J/mz5z246aSi3i2p2/0zGj82WDrtFjar1O7klO4dkfimUJcWnbho0rgr1vntFfmvFflvGOZdFKXZkOUemnmv2XkuWWVe2ziqlXnt1Tr0HDpwl6ObmCkbEKqhVyOc2jdoVHmuljfrmDq0nPapWDUnErqy3XjtWXesXLrzHjz34rqzYfmw3fy4YrqyYDevW/dzoTIhkndsXLRsIneuHjlyIzQroTjuXjlyYfktWvw2prhvoHTmGfx45j3773TuYT/25LdijyKf321oXU+Nm3cumXfuWLtwlzpwVz40FvpvlvqvFfouFXjrlHipEjcmEfknEXPbzfbZyzZQR/YMBrWKBrhJhLdHxDTGg5HV4xBT4YYKYaWk4SDgYIWIYBybH0qLn1KS3tlZHpNS3WGfHIcHXEwLHAnF28rKW07NGuzn2pNQ2ruzWnDrGnuy2jryGjAnGgoH2j1x2RCNGPcrmIsEGGQdl/pu17YtV7FoV3muVxoRVzWqFvSmVp2SVbyw1XbkVTuvFPfo1PgmVPpt1LcnFLWkVLlp1F7W1HpsU92QE5oMUtFAUrpqUjnjUFOAEHUgz+DUj14FzvbczieMTdhATfodjXWcDXcbjXVcTS/Xi/hay7WXS3cWS3vYyvaVSrUVymnJSjXSyeKDSbNSiWfHCPMTyLFQiHkSR/lPxvVLRrPLBnUJRfUHhbaJxXVGxTZJxPNFhBdOhm/AAAAWXRSTlMABQIU/hIJ/v79/Pj29PPx4cC6s7CNfmxZWRv+/v7+/v7+/v78/Pr6+fPz8vHq6ujl5eTj4ODe2NTQzMW6ubKsnJeQkJCJiIOBgX9ubGpoW1lMREM0JR8dDgvYx1gAAAE7SURBVBjTYgADJmZJQUFJZiYGOGD2EzLV1jIT8paCibCJ86zctGPD1D4ecUaICKuPyYLMYznZOfNqzP0jwEJBOt1KB4/mHjqZ3dGsHwxW5M4Zk5l/PPdIQcGMShUPVqBlgQLlMSvyDq+P3HVidjWnkQQTA5MXV1SFYtb+jZGrl02si2J3Y2JgFMmILl68efueLVvXLSqLXirCCBgDow1HT+GS/AP7srblLS+K5bIHCjmodpXUr929d+eaVb3SsuouQCHhufPjShsbJk/rrK2KW8hiBxRyVkvnkI9tnaDQJDNFOU1DDOjRMEfe9Mjpiewz5RIzZmmKMoPcKqGbkJqSkBSfnDqpXS+ACeRpJ76W/uSUpDlpLPFtfK5soLAKFbU05Odm4eblN7YWk4KEGWOIp62FgYCVsG84SAAAL7BaooX965sAAAAASUVORK5CYII=");
}
</style>