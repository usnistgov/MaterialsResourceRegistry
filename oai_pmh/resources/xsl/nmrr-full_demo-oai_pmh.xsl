<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
	xmlns:nr="http://schema.nist.gov/xml/res-md/1.0wd-02-2017">
	<xsl:output method="html" indent="yes" encoding="UTF-8" />

	<xsl:template match="/">
		<div class="white-bg">
			<xsl:variable name="title"  select="//nr:Resource/nr:identity/nr:title"/>
			{% if oai_pmh %}
                <xsl:text disable-output-escaping="yes">&lt;a class="title" href="</xsl:text>
				<xsl:text disable-output-escaping="yes">{% url 'oai-explore-detail-result-keyword' id %}</xsl:text>
				<xsl:text disable-output-escaping="yes">" &gt;</xsl:text>
					<xsl:choose>
						<xsl:when test="$title!=''">
							<strong><xsl:value-of select="$title"/></strong>
						</xsl:when>
						<xsl:otherwise>
							<strong class="italic">Untitled</strong>
						</xsl:otherwise>
					</xsl:choose>
				<xsl:text disable-output-escaping="yes">&lt;/a&gt;</xsl:text>
			{% else %}
				{% if local_id %}
				<xsl:text disable-output-escaping="yes">&lt;a class="title" href="</xsl:text>
				<xsl:text disable-output-escaping="yes">{% url 'expore-index-keyword' %}?Resource.@localid={{local_id}}</xsl:text>
				<xsl:text disable-output-escaping="yes">" &gt;</xsl:text>
                    <xsl:choose>
                        <xsl:when test="$title!=''">
                            <strong><xsl:value-of select="$title"/></strong>
                        </xsl:when>
                        <xsl:otherwise>
                            <strong class="italic">Untitled</strong>
                        </xsl:otherwise>
                    </xsl:choose>
				<xsl:text disable-output-escaping="yes">&lt;/a&gt;</xsl:text>
				{% else %}
                <xsl:text disable-output-escaping="yes">&lt;a class="title" href="</xsl:text>
				<xsl:text disable-output-escaping="yes">{% url 'explore-detail-result-keyword' id %}</xsl:text>
				<xsl:text disable-output-escaping="yes">" &gt;</xsl:text>
					<xsl:choose>
						<xsl:when test="$title!=''">
							<strong><xsl:value-of select="$title"/></strong>
						</xsl:when>
						<xsl:otherwise>
							<strong class="italic">Untitled</strong>
						</xsl:otherwise>
					</xsl:choose>
				<xsl:text disable-output-escaping="yes">&lt;/a&gt;</xsl:text>
				{% endif %}
			{% endif %}
			<div class="black">
				<xsl:variable name="creators" select="//nr:Resource/nr:providers/nr:creator" />
				<xsl:variable name="publisher" select="//nr:Resource/nr:providers/nr:publisher"/>
				<xsl:call-template name="join">
					<xsl:with-param name="list" select="$creators" />
					<xsl:with-param name="separator" select="', '" />
				</xsl:call-template>
				<xsl:if test="( ($creators!='') and ($publisher!='') )">
					<xsl:text> - </xsl:text>
				</xsl:if>
				<xsl:value-of select="$publisher"/>
			</div>
			<xsl:variable name="url" select="//nr:Resource/nr:content/nr:landingPage" />
			<a target="_blank" href="{$url}"><xsl:value-of select="$url"/></a>
			<xsl:variable name="idw"  select="'{{id}}'" />
			<a data-toggle="collapse" data-target="#{$idw}"
			  aria-expanded="false" aria-controls="{$idw}" class="collapsed">
				<i class="fa fa-chevron-up" />
				<i class="fa fa-chevron-down" />
			</a>
			<div class="collapseXSLT collapse" id="{$idw}">
					<xsl:apply-templates select="//*[not(*)]"/>
					<!--<xsl:variable name="terms" select="//nr:Resource/nr:access/nr:policy/nr:terms" />-->
					<!--<xsl:if test="$terms!=''">-->
						<!--<xsl:text>Terms: </xsl:text>-->
						<!--<xsl:value-of select="$terms"/>-->
						<!--<br/>-->
					<!--</xsl:if>-->
			</div>
			<xsl:variable name="subject" select="//nr:Resource/nr:content/nr:subject" />
			<xsl:if test="$subject!=''">
				<div class="keywords">
					<xsl:text>Subject keyword(s): </xsl:text>
					<xsl:call-template name="join">
						<xsl:with-param name="list" select="$subject" />
						<xsl:with-param name="separator" select="', '" />
					</xsl:call-template>
				</div>
			</xsl:if>
			<div class="black">
				<p class="description">
					<xsl:value-of select="//nr:Resource/nr:content/nr:description"/>
				</p>
			</div>
			{% if oai_pmh %}
			<div class="harvested">↳ Harvested from
                <xsl:text disable-output-escaping="yes">&lt;a href="</xsl:text>
				<xsl:text disable-output-escaping="yes">{{registry_url}}</xsl:text>
				<xsl:text disable-output-escaping="yes">" &gt;</xsl:text>
                    <text>{{registry_name}}</text>
                <xsl:text disable-output-escaping="yes">&lt;/a&gt;</xsl:text>
			</div>
			{% endif %}
			<br/>
		</div>
	</xsl:template>

	<xsl:template name="join">
		<xsl:param name="list" />
		<xsl:param name="separator"/>

		<xsl:for-each select="$list">
			<xsl:value-of select="." />
			<xsl:if test="position() != last()">
				<xsl:value-of select="$separator" />
			</xsl:if>
		</xsl:for-each>
	</xsl:template>

	<xsl:template match="//*[not(*)]">
		<xsl:variable name="name" select="name(.)" />
		<xsl:variable name="value" select="." />
		<xsl:variable name="arg" select="@type" />
		<xsl:if test="( (contains($name, 'URL')) or (starts-with($value, 'https://')) or (starts-with($value, 'http://')) )">
			<xsl:if test="$value!=''">
				<xsl:value-of select="$name"/>
				<xsl:text>: </xsl:text>
				<a target="_blank" href="{$value}"><xsl:value-of select="$value"/></a>
				<br/>
			</xsl:if>
		</xsl:if>
	</xsl:template>

</xsl:stylesheet>
